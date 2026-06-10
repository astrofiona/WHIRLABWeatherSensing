# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 13:24:35 2026

@author: tisfi
"""
import os
import sys

srcpath = os.path.realpath('SourceFiles')
sys.path.append(srcpath)

import warnings # this is for GUI warnings
warnings.filterwarnings("ignore")

from tevisainst import TEVisaInst

import numpy as np
from scipy import special

import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import keyboard
import time
import datetime

import commpy.utilities as util
import commpy.filters as FIL

#tabor1=0
##########Transmitter Params##########
sf=1e9 # sampling frequency

chan = 1
Interpolation = 8
data_type = np.uint16 
half_dac=int(65535/2)
samp = 16;
beta=.5
######################################

N = 839  # Length of Zadoff-Chu sequence
u = 25  # Root of ZC sequence
t = np.arange(N)
signal_length=1000000
zadoff_chu = np.exp(-1j * np.pi * u * t * (t + 1) / N)
#########Reciever Params##############
rsf=4.5e9# receiver sampling frequency
framelen = 480000
numframes=1
######################################

def connect():
    inst = TEVisaInst('192.168.100.111')
    inst.default_paranoia_level = 2 # good for debugging
    #inst.send_scpi_cmd('*CLS; *RST')
    return inst


def writememdir(inst,I,chan):
    #inst.send_scpi_cmd('*CLS; *RST')
    #inst.send_scpi_cmd(':DIG:ACQ:ZERO:ALL')
    roundingfactor1=(int)((np.ceil(len(I)/128))*128-len(I))
    I=np.array(list(I)+(roundingfactor1*[0]))
    segLen=len(I)#1024

    d = 2.*(I - np.min(I))/np.ptp(I)-1
    I = (d) *.9* half_dac+half_dac

    s = I
    signal = np.zeros(len(s)*2)
    signal[::2] = s#half_dac*1.8
    signal[1::2] = half_dac
    s = signal
    s = s.astype(data_type)
    inst.send_scpi_cmd(':INST:CHAN {0}'.format(chan))
    inst.send_scpi_cmd(':TRAC:DEF {0},'.format(chan) + str(len(s)))
    inst.send_scpi_cmd(':TRAC:SEL {0}'.format(chan))
    # download the waveform to the selected segment
    #what does the line right below this comment do I couldnt find it in the manual~Jack
    inst.write_binary_data('*OPC?; :TRAC:DATA', s)
    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)
    
def transmit(inst,vpp,chan,cf):


    inst.send_scpi_cmd(':INST:CHAN {0}'.format(chan))
    inst.send_scpi_cmd(':SOUR:FUNC:MODE:SEGM {0}'.format(chan))
    inst.send_scpi_cmd(':SOUR:VOLT {0}'.format(vpp))
    inst.send_scpi_cmd(':OUTP ON')

def config(inst):
    inst.send_scpi_cmd('*CLS; *RST')
    
#    inst.send_scpi_cmd(':SOUR:INT ' + str(Interpolation))
#    resp = inst.send_scpi_query(':SYST:ERR?')
#    print(resp)

    #inst.send_scpi_cmd(':SOUR:NCO:CFR1 1000MHZ'.format(cf))#added CFR1 applies blw
    inst.send_scpi_cmd(':SOUR:FREQ 2.5e9')
    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)

    inst.send_scpi_cmd(':SOUR:INT ' + str('X8'))
    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)

    # set NCO frequency of CH1
    inst.send_scpi_cmd(':INST:CHAN 1')
    inst.send_scpi_cmd(':SOUR:NCO:CFR1 1000.0e6')#added CFR1 applies blw
    #inst.send_scpi_cmd(':SOUR:NCO:CFR1 0')#added CFR1 applies blw
    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)

    inst.send_scpi_cmd(':DIG:MODE SING')
    time.sleep(.5)
    inst.send_scpi_cmd(':DIG:FREQ 4500MHZ')
    time.sleep(.5)
    # Allocate four frames of 4800 samples

    
    cmd = ':DIG:ACQuire:FRAM:DEF {0},{1}'.format(numframes, framelen)
    inst.send_scpi_cmd(cmd)
    time.sleep(.5)
    # Select the frames for the capturing 
    # (all the four frames in this example)
    capture_first, capture_count = 1, numframes
    cmd = ":DIG:ACQuire:FRAM:CAPT {0},{1}".format(capture_first, capture_count)
    inst.send_scpi_cmd(cmd)
    time.sleep(.5)
    
    # Set Trigger level to 0.2V
    #inst.send_scpi_cmd(':DIG:TRIG:LEV1 0.1')
    
    # Enable capturing data from channel 1
    inst.send_scpi_cmd(':DIG:CHAN:SEL 1')
    time.sleep(.1)
    inst.send_scpi_cmd(':DIG:CHAN:STATE ENAB')
    time.sleep(.5)
    # Select the external-trigger as start-capturing trigger:
    inst.send_scpi_cmd(':DIG:TRIG:SOURCE CPU')
    
    
    # Clean memory 
    #inst.send_scpi_cmd(':DIG:ACQ:ZERO:ALL')
    
    resp = inst.send_scpi_query(':SYST:ERR?')
    time.sleep(1)
    # set modulation to ONE
    inst.send_scpi_cmd(':SOUR:IQM ONE')
    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)

    # chande DAC clock to 9000Hz
    inst.send_scpi_cmd(':SOUR:FREQ ' + str(8e9))
    resp = inst.send_scpi_query(':SYST:ERR?')
   # inst.send_scpi_cmd(':SOUR:NCO:CFR1 0')#added CFR1 applies blw
    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)

    print(resp)

    # set modulation to ONE
    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)


####Rx######
def capture(inst,chan):
    sig =[]
    inst.send_scpi_cmd(':DIG:INIT ON')
    inst.send_scpi_cmd(':DIG:TRIG:IMM')
    time.sleep(.51)
    inst.send_scpi_cmd(':DIG:INIT OFF')
    inst.send_scpi_cmd(':DIG:DATA:SEL ALL')
    inst.send_scpi_cmd(':DIG:DATA:TYPE FRAM')
    resp = inst.send_scpi_query(':DIG:DATA:SIZE?')
    num_bytes = np.uint32(resp)
    inst.send_scpi_cmd(':DIG:CHAN:SEL {0}'.format(chan))
    wavlen = num_bytes // 2
    sig = np.zeros(wavlen, dtype=np.uint16)
    time.sleep(.51)
    inst.read_binary_data(':DIG:DATA:READ?', sig, num_bytes)
    return sig
def savefile(data,filename):
    np.save(filename,data)
def digconfig3(inst,numframes,framelen):
    #global tabor1
    #inst = connect()
    #tabor1=inst
    #inst.send_scpi_cmd('*CLS; *RST')

    #tabor2.send_scpi_cmd(':DIG:FREQ:SOUR EXT')
    inst.send_scpi_cmd(':DIG:MODE SING')
    time.sleep(.5)
    inst.send_scpi_cmd(':DIG:FREQ 4100MHZ')
    time.sleep(.5)
    # Allocate four frames of 4800 samples

    
    cmd = ':DIG:ACQuire:FRAM:DEF {0},{1}'.format(numframes, framelen)
    inst.send_scpi_cmd(cmd)
    time.sleep(.5)
    # Select the frames for the capturing 
    # (all the four frames in this example)
    capture_first, capture_count = 1, numframes
    cmd = ":DIG:ACQuire:FRAM:CAPT {0},{1}".format(capture_first, capture_count)
    inst.send_scpi_cmd(cmd)
    time.sleep(.5)
    
    # Set Trigger level to 0.2V
    #inst.send_scpi_cmd(':DIG:TRIG:LEV1 0.1')
    
    # Enable capturing data from channel 1
    inst.send_scpi_cmd(':DIG:CHAN:SEL 1')
    time.sleep(.1)
    inst.send_scpi_cmd(':DIG:CHAN:STATE ENAB')
    time.sleep(.5)
    # Select the external-trigger as start-capturing trigger:
    inst.send_scpi_cmd(':DIG:TRIG:SOURCE CPU')
    
    
    # Clean memory 
    #inst.send_scpi_cmd(':DIG:ACQ:ZERO:ALL')
    
    resp = inst.send_scpi_query(':SYST:ERR?')
    time.sleep(1)
    return inst
    #print(resp)
    #print("Set Digitizer: DUAL mode; internal Trigger")
