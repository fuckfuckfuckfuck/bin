#!/usr/bin/env python
# -*- coding: utf-8 -*-

## scan data
import string
import re
import numpy as np

# mkt_pattern = "(\d+)\s\[(\d+)\]\s([A-Z]+)\stest\s<>\s-\s(\d+)\s(\w+)\s+(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d\d:\d\d:\d\d)\s(\d+)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+\.?\d*[eE]?[+]?\d*)\s(\d+)"
# line = "18246655 [139707331954432] DEBUG test <> - 20140627 au1408   263.25 264.05 263.8 212 262.45 263.25 262.45 16 4.2072e+06 220 1.79769e+308 1.79769e+308 277.25 250.8 02:00:15 0 262.75 2 263.3 1 262950 255957"
line = "09:14:00|300|3499.8|3659|3841730000.0|118117|3503.0|741|778717000.0|67395"
pattern = "(\d+:\d+:\d+)\|(\d+)\|(\d+\.?\d*)\|(\d+)\|(\d+\.?\d*[eE]?[+]?\d*)\|(\d+)\|(\d+\.?\d*)\|(\d+)\|(\d+\.?\d*[eE]?[+]?\d*)\|(\d+)"
p = re.compile(pattern)

##re = p.match(line)
##re = re.groups()

##class tick:
##    def __init__(self,updatetime,UpdateMillisec,LastPrice,Volume,Turnover,OpenInterest):
##        self.__updatetime = updatetime
##        self.__UpdateMillisec = UpdateMillisec
##        self.__LastPrice = LastPrice
##        self.__Volume = Volume
##        self.__Turnover = Turnover
##        self.__OpenInterest = OpenInterest

##def scanData(fstr):        
fstr = open("0.txt",'r')
lines = fstr.readlines()
re = []
for row in lines:
    ret2 = []
    ret2 = p.match(row)    
    ret2 = ret2.groups()
    re.append(ret2)

##re2 = np.zeros((len(re),1), dtype=('a8,i4,f8,i4,f8,i4,f8,i4,f8,i4'))
re2 = np.zeros((len(re),8), dtype=('f8'))
re3 = np.zeros((len(re),1), dtype=('a8,i4'))
for i in xrange(len(re)):
    re3[i,0][0] = re[i][0]
    re3[i,0][1] = string.atoi(re[i][1])
    re2[i,0] = string.atof(re[i][2])
    re2[i,1] = string.atoi(re[i][3])
    re2[i,2] = string.atof(re[i][4])
    re2[i,3] = string.atoi(re[i][5])
    re2[i,4] = string.atof(re[i][6])
    re2[i,5] = string.atoi(re[i][7])
    re2[i,6] = string.atof(re[i][8])
    re2[i,7] = string.atoi(re[i][9])
    

##    re1.append(ret[0])
##    ret.append(string.atoi(ret[1]))
##    ret.append(string.atof(ret[2]))
##    ret.append(string.atoi(ret[3]))
##    ret.append(string.atof(ret[4]))
##    ret.append(string.atoi(ret[5]))
##    ret.append(string.atof(ret[6]))
##    ret.append(string.atoi(ret[7]))
##    ret.append(string.atof(ret[8]))
##    ret.append(string.atoi(ret[9]))    
##    for i in xrange(9):
##        ret.append(row[i])
##    re2.append(ret)



fstr.close()

