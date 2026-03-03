# -*- coding: utf-8 -*-
"""
Created on Thu Feb 19 13:05:19 2026

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

import matplotlib.pyplot as plt
from matplotlib.widgets import Button

import keyboard
import time
import datetime

import commpy.utilities as util
import commpy.filters as FIL

# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 18:43:55 2025

@author: Rutgers University
"""
     

def connect():
    inst = TEVisaInst('192.168.100.111')
    inst.default_paranoia_level = 2 # good for debugging
    inst.send_scpi_cmd('*CLS; *RST')
    return inst


def writememdir(inst,I,chan):
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


    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)


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

    print(resp)

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

    # chande DAC clock to 9000Hz
    
    resp = inst.send_scpi_query(':SYST:ERR?')
    print(resp)
    inst.send_scpi_cmd(':INST:CHAN {0}'.format(chan))
    inst.send_scpi_cmd(':SOUR:FUNC:MODE:SEGM {0}'.format(chan))
    inst.send_scpi_cmd(':SOUR:VOLT {0}'.format(vpp))
    inst.send_scpi_cmd(':OUTP ON')
    
 
sf=1e9 # sampling frequency
rsf=4e9# receiver sampling frequency
chan = 1
Interpolation = 4
data_type = np.uint16 
half_dac=int(65535/2)
samp = 16;
#ruid = 218006192
#np.random.seed(ruid)
x = np.random.randint(0, 2, 100000)*2-1
x_samp = np.real(util.upsample(x,samp))
#t = np.linspace(1/sf, len(x_samp)*1/sf,len(x_samp))
#sin = np.sin(np.sin(2*np.pi*100*t))
#st=np.convolve(np.real(x_samp),np.ones(10))

beta = 0.5 # roll off factor 
[pst_a,pst_t] = FIL.rrcosfilter(9*samp, beta, samp, 1) # rrc cosine filters
st = np.convolve(pst_t, x_samp)



# establish barker code, this is our training sequence
#num_channel_coef = 4;
#bc13 = np.array([1, -1, -1, -1, -1, 1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, 1, 1, 1, -1, 1, 1, 1, 1, 1, -1, -1, 1, -1, -1, 1])
#bc13up = util.upsample(bc13, samp)
#bc13up = np.convolve(bc13up.astype('float64'), pst_t)
#stb = np.concatenate((bc13up.astype('float64'), st.astype('float64')), axis=0)

    
y = connect()
writememdir(y, st, 1)
transmit(y, 0.55, 1, 1e9)


# receiver
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
    inst.read_binary_data(':DIG:DATA:READ?', sig, num_bytes)
    return sig
def savefile(data,filename):
    np.save(filename,data)
def digconfig3(inst):
    global framelen
    #inst.send_scpi_cmd('*CLS; *RST')

    #tabor2.send_scpi_cmd(':DIG:FREQ:SOUR EXT')
    inst.send_scpi_cmd(':DIG:MODE SING')
    inst.send_scpi_cmd(':DIG:FREQ 4000MHZ')
    
    # Allocate four frames of 4800 samples
    numframes=1
    framelen = 480000
    cmd = ':DIG:ACQuire:FRAM:DEF {0},{1}'.format(numframes, framelen)
    inst.send_scpi_cmd(cmd)
    
    # Select the frames for the capturing 
    # (all the four frames in this example)
    capture_first, capture_count = 1, numframes
    cmd = ":DIG:ACQuire:FRAM:CAPT {0},{1}".format(capture_first, capture_count)
    inst.send_scpi_cmd(cmd)
    
    # Set Trigger level to 0.2V
    #inst.send_scpi_cmd(':DIG:TRIG:LEV1 0.1')
    
    # Enable capturing data from channel 1
    inst.send_scpi_cmd(':DIG:CHAN:SEL 1')
    inst.send_scpi_cmd(':DIG:CHAN:STATE ENAB')
    # Select the external-trigger as start-capturing trigger:
    inst.send_scpi_cmd(':DIG:TRIG:SOURCE CPU')
    
    
    # Clean memory 
    inst.send_scpi_cmd(':DIG:ACQ:ZERO:ALL')
    
    resp = inst.send_scpi_query(':SYST:ERR?')
    #print(resp)
    #print("Set Digitizer: DUAL mode; internal Trigger")

# Connect to and configure Tabor
#connect()
rxclk = 4000
txclk = 1000
ratio = rxclk/txclk

#capture(tabor2,1)
tabor1= y


elem=[1,3,2,4]
angle=0
d=.166  
c=299_792_458
f=900e6
estimate =[1,1]
digconfig3(tabor1)
sig=capture(tabor1,1)
sig=(sig*1/4096)*0.5-0.25
plt.plot(np.fft.fftshift(np.fft.fft(sig)/len(sig)))
plt.show()
def process_sj(samples,rsf,wl,overlap):
    pwr=np.zeros(wl)
    numwindows=int((len(samples)-(wl*(1-overlap))))/(wl*overlap)
    for i in range(int(numwindows)):
        window_signal=samples[i*int(wl*overlap):(i+1)*int(wl*overlap)+int(wl*(1-overlap))]
        fourierTransform = np.fft.fft(window_signal)/len(window_signal)
        pwr=pwr+(10*np.log10(np.square(abs(fourierTransform))))
    fvec=(np.linspace(0, wl-1,wl)-wl/2)*(rsf/wl)
    #fvec=np.arange(rsf/-2, rsf/2, rsf/wl)
    return((pwr/numwindows),fvec)



[pwrVec,fvec]=process_sj(sig,4e9,4800,0.5)
samplen = len(pwrVec)
# np.save('wtr',pwrVec)
# print('capturing')
rsf = 4e9
tsf = 1e9
cfreq = 1e9
cfreq2 = 1.75e9

ctrlVec = np.load('ctrl.npy')
wtrVec = np.load('wtr.npy')
fres=(rsf/samplen)
bw = (tsf/samp)+(1+beta)
windInt = [int(((len(ctrlVec)/2)+(cfreq/fres)) - (bw/fres)/2)-200,int(((len(ctrlVec)/2)+(cfreq/fres)) + (bw/fres)/2)+200]
windInt2 = [int(((len(ctrlVec)/2)+(cfreq2/fres)) - (bw/fres)/2)-200,int(((len(ctrlVec)/2)+(cfreq2/fres)) + (bw/fres)/2)+200]
plt.plot(fvec[windInt2[0]:windInt2[1]],np.fft.fftshift(ctrlVec)[windInt2[0]:windInt2[1]])
plt.plot(fvec[windInt2[0]:windInt2[1]], np.fft.fftshift(wtrVec)[windInt2[0]:windInt2[1]])
plt.legend(['Control', 'w/ Water'])
plt.title('FFT of Received Signal w[k] with RRC Filter')




plt.show()
tabor1.close_instrument()




