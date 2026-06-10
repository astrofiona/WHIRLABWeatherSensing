# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 13:24:19 2026

@author: tisfi
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Feb 19 13:05:19 2026

@author: tisfi
"""

from rainfunc import *


x = np.random.randint(0, 2, signal_length)*2-1
x_samp = np.real(util.upsample(x,samp))
offset = np.random.randint(N, signal_length - N)

# roll off factor 
filter_size=9
[pst_a,pst_t] = FIL.rrcosfilter(filter_size*samp, beta, samp, 1) # rrc cosine filters
st = np.convolve(pst_t, x_samp)   
st[offset:offset+N] += abs(zadoff_chu)
tabor1 = connect()
writememdir(tabor1, st, 1)
transmit(tabor1, 0.5, 1, 1e9)
tabor1.close_instrument()

