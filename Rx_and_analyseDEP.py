from rainfunc import *
def process_sj(samples,rsf,wl,overlap):
    pwr=np.zeros(wl)
    numwindows=int((len(samples)-(wl*(1-overlap))))/(wl*overlap)
    for i in range(int(numwindows)):
        window_signal=samples[i*int(wl*overlap):(i+1)*int(wl*overlap)+int(wl*(1-overlap))]
        fourierTransform = np.fft.fft(window_signal)/len(window_signal)
        pwr=pwr+10*np.log10(np.square(abs(fourierTransform)))
    fvec=(np.linspace(0, wl-1,wl)-wl/2)*(rsf/wl)
    #fvec=np.arange(rsf/-2, rsf/2, rsf/wl)
    return((pwr/numwindows),fvec)
def qfunc(f):
    return 0.5 - 0.5*special.erf(f/np.sqrt(2)) # Q(f) = 0.5 - 0.5 erf(f/sqrt(2))
tabor1 = connect()
#digconfig3(tabor1,framelen,numframes)
ratio = sf/rsf #ratio of samples transmitted to samples recieved

# sig=capture(tabor1,1)
# sig=(sig*1/4096)*0.5-0.25
# sig=sig-np.mean(sig)
# # plt.plot(np.fft.fftshift(np.fft.fft(sig)/len(sig)))
# # plt.show()



# [pwrVec,fvec]=process_sj(sig,rsf,4800,0.5)
# samplen = len(pwrVec)
# # np.save('wtr',pwrVec)
# # print('capturing')

# cfreq = 1e9
# plt.plot((np.linspace(0, framelen-1,framelen)-framelen/2)*(rsf/framelen),abs(np.fft.fftshift(np.fft.fft(sig))))
# plt.show()
# np.save('test3_3',pwrVec)
# ctrlVec = np.load('test3_3.npy')#-noisrm
# fres=(rsf/samplen)
# bw = (sf/samp)*(1+beta)
# windInt = [int(((len(ctrlVec)/2)+(cfreq/fres)) - (bw/fres)/2)-80,int(((len(ctrlVec)/2)+(cfreq/fres)) + (bw/fres)/2)+80]
# # windInt2 = [int(((len(ctrlVec)/2)+(cfreq2/fres)) - (bw/fres)/2)-200,int(((len(ctrlVec)/2)+(cfreq2/fres)) + (bw/fres)/2)+200]
# plt.plot(fvec[windInt[0]:windInt[1]],np.fft.fftshift(ctrlVec)[windInt[0]:windInt[1]])
# plt.title('FFT of Received Signal w[k] with RRC Filter [Windowed at 1 GHz]')
# # plt.plot(fvec[windInt2[0]:windInt2[1]], np.fft.fftshift(wtrVec)[windInt2[0]:windInt2[1]])
# plt.show()
# plt.plot(fvec,ctrlVec)
# plt.title('FFT of Received Signal w[k] with RRC Filter')
# plt.show()
# tabor1.close_instrument()

N = 1e6
T = (samp*N)/sf
# pwr = (1/T)*np.sum(np.square(sig[0:samp]))
# pwrdB = 10*np.log10(pwr)
# print(pwrdB)
sigma = 3
tau = 10.7
detections = 0
pmr_list = []
cnum=100
tabor1.send_scpi_cmd(':OUTP ON')
for i in range(1,cnum):
    sig=capture(tabor1,1)
    sig=(sig*1/4096)*0.5-0.25
    sig=sig-np.mean(sig)
    [pwrVec,fvec] = process_sj(sig,rsf,4800,0.5)
    cfreq = 1e9
    samplen = len(pwrVec)
    fres=(rsf/samplen)
    bw = (sf/samp)*(1+beta)
    windInt = [int(((len(pwrVec)/2)+(cfreq/fres)) - (bw/fres)/2)-80,int(((len(pwrVec)/2)+(cfreq/fres)) + (bw/fres)/2)+80]
    peak_val = float(np.max(pwrVec))
    # mean_val = float(np.mean(pwrVec))
    pmr_list = np.append(pmr_list,peak_val)
    if peak_val > tau:
        detections += 1
np.save("on100.npy",pmr_list)
tabor1.send_scpi_cmd(':OUTP OFF')
for i in range(1,cnum):
    sig=capture(tabor1,1)
    sig=(sig*1/4096)*0.5-0.25
    sig=sig-np.mean(sig)
    [pwrVec,fvec] = process_sj(sig,rsf,4800,0.5)
    cfreq = 1e9
    samplen = len(pwrVec)
    fres=(rsf/samplen)
    bw = (sf/samp)*(1+beta)
    windInt = [int(((len(pwrVec)/2)+(cfreq/fres)) - (bw/fres)/2)-80,int(((len(pwrVec)/2)+(cfreq/fres)) + (bw/fres)/2)+80]
    peak_val = float(np.max(pwrVec))
    # mean_val = float(np.mean(pwrVec))
    pmr_list = np.append(pmr_list,peak_val)
    if peak_val > tau:
        detections += 1
np.save("null100.npy",pmr_list)
print(detections)
plt.show()
tabor1.close_instrument()