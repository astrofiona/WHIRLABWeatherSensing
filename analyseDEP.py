# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 12:47:35 2026

@author: sbjoh
"""
from rainfunc import *
null=np.load("null100.npy")
txcase=np.load("on100.npy")
allnums=np.append(null,txcase)
errsaved=1
threshsaved=0
for i in allnums:
    thresh=i+.00001
    err=(np.mean(((null>thresh)))+np.mean(((txcase>thresh)==0)))/2
    if errsaved>err:
        errsaved=err
        threshsaved=thresh
print(threshsaved)
print(errsaved)