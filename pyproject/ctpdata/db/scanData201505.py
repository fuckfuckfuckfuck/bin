#!/usr/bin/env python
# -*- coding: utf-8 -*-

## scan data
import string
import re
import numpy as np
import datetime as dtime
import matplotlib.pyplot as plt

# from utility import timeFil
from utility import sql_jzt_tSectors_insert
from utility import sql_jzt_tContracts_insert
from utility import sql_jzt_tTradingday_insert
from utility import sql_jzt_continu
from utility import trinity
# from utility import my_corr_matrix
from utility import sql_jzt_continu_select
from utility import my_str
from utility import sql_jzt_mktvital_insert 

import os
import sqlite3
import logging
from patterns import p_jztlog
from patterns import p_jzt


# params
ABS_DIR = "E:\\dataTickCmmdt\\"
# datestrs = ["20150430"]
# datestrs = ["20150511"]
# datestrs = ["20150512"]
# datestrs = ["20150513"]
datestrs = ["20150430","20150511","20150512","20150513","20150514","20150515"]
DB_SQLITE_PATH = "D:\\bin\\pyproject\\ctpdata\\db\\jzt_onemin.db"
# logging
exchanges = ("DQ","SQ","ZQ","ZJ")
scanErrorFile = open("error_jzt.txt", 'a')
FORMAT = '%(asctime)-15s - %(levelname)-6s - %(message)s'
logging.basicConfig(filename='test_jzt.log', format=FORMAT, level=logging.DEBUG)
sqlite_logger = logging.getLogger('test')
# result
list_log = []
list_sectors = []
list_symbols = []

# # given setting
# list_continuous = ["AU30","AU31","AU32","AU33","AU34","AU35"]
# len_continu = len(list_continuous)
# len_continu_row = 226

# list_continu_data = np.zeros((len_continu_row,4),dtype='f8')
# array_continu = np.zeros((len_continu_row,len_continu),dtype='f8')
# list_continu_re1 = np.zeros((len_continu,3),dtype='f8')

# prepare for db
try:
    sqlite_conn = sqlite3.connect(DB_SQLITE_PATH)
except sqlite3.Error as err:
    print "connection failed."
    sqlite_logger.error("conn. failed, ret = %s" % err.args[0])
    # return
sqlite_cursor = sqlite_conn.cursor()


def generate_x_y(prob_map):
    s = prob_map.shape
    x, y = np.meshgrid(np.arange(s[0]), np.arange(s[1]))
    return x.ravel(), y.ravel()

def heatmap(prob_map):
    x, y = generate_x_y(prob_map)
    plt.figure()
    plt.hexbin(x, y, C=prob_map.ravel())

# probs = np.random.rand(200, 200)
# heatmap(probs)
# plt.show()

####################################################################
def interval_statistics(left, right,re2,re3,re4):    
    # (tmp_i_last,i]   
    # re3 must exist in closure?
    # sqlite_logger
    if (left > right):
        sqlite_logger.error("Left:%(left)s is bigger than right:%(right)s. Exit." % {'left':left, 'right':right})
        return
    elif (left == right):
        open = re3[right][0]
        close = open
        high = open
        low = open
        volume = re4[right][0]
        amount = re4[right][1]
        openint = re4[right][2]
    else:
        open = re3[left+1][0]
        close = re3[right][0]
        high = -99999
        low = 999999
        # volume = 0
        volume = re4[right][0]
        amount = re4[right][1]
        openint = re4[right][2]
        for i in range(left+1,right+1):
            # the case when left++ > right is avoided by demanding left<right
            high = max(high, re3[i][0])
            low = min(low, re3[i][0])
            # volume = volume + re4[i][0]
    return (open,high,low,close,volume,amount,openint)
##class tick:
##    def __init__(self,updatetime,UpdateMillisec,LastPrice,Volume,Turnover,OpenInterest):
##        self.__updatetime = updatetime
##        self.__UpdateMillisec = UpdateMillisec
##        self.__LastPrice = LastPrice
##        self.__Volume = Volume
##        self.__Turnover = Turnover
##        self.__OpenInterest = OpenInterest




def scan_insert(absdir, file, symbol):
    ## sqlite_logger
    ## scanErrorFile
    ## sqlite_

    # 1) scan ticks
    absfile = absdir + "\\" + file
    fstr = open(absfile, 'r')
    lines = fstr.readlines()
    ree = []
    for row in lines:
        ret2 = p_jzt.match(row)    
        if (None == ret2):
            scanErrorFile.write(line+'\n')        
            continue
        ret2 = ret2.groups()
        ree.append(ret2)   

    ## re2 = np.zeros((len(ree),1), dtype=('a8,i4,f8,i4,f8,i4,f8,i4,f8,i4'))
    ## re2 = np.zeros((len(ree),1), dtype='datetime64')
    re2 = np.zeros((len(ree),1), dtype=('i4,i4'))
    re3 = np.zeros((len(ree),1), dtype = ('f8'))
    re4 = np.zeros((len(ree),4), dtype = ('i4'))
    for i in xrange(len(ree)):
        re2[i,0][0] = string.atoi(ree[i][0])*10000 + string.atoi(ree[i][1])*100 + string.atoi(ree[i][2])
        re2[i,0][1] = string.atoi(ree[i][3])*10000 + string.atoi(ree[i][4])*100 + string.atoi(ree[i][5])
        ## re2[i] = np.datetime64(ree[i][0]+'-'+timeFill(ree[i][1])+'-'+timeFill(ree[i][2])+'T'+timeFill(ree[i][3])+':'+ree[i][4]+':'+ree[i][5])
        ## re2[i] = dtime.datetime(string.atoi(ree[i][0]),string.atoi(ree[i][1]),string.atoi(ree[i][2]),string.atoi(ree[i][3]),string.atoi(ree[i][4]),string.atoi(ree[i][5]))
        re3[i] = string.atof(ree[i][6])
        re4[i,0] = string.atoi(ree[i][7])
        re4[i,1] = string.atoi(ree[i][8])
        re4[i,2] = string.atoi(ree[i][9])
        re4[i,3] = string.atoi(ree[i][10])
    
    # 2) close
    try:
        fstr.read()
    finally:
        fstr.close()
    
    # 3) aggregation, one min
    tmp_idx = []
    tmp_i_last = 0
    tmp_i_num = int(re2[0,0][1]/100)
    tmp_bench = len(re2)
    tmp_data = []
    for i in range(1, tmp_bench):
        if ((tmp_bench - 1) != i):
            tmp = int(re2[i][0][1] / 100)
            if (tmp_i_num != tmp):
                # (tmp_i_last,i]       
                tmp_data_1 = interval_statistics(tmp_i_last, i,re2,re3,re4)
                tmp_data.append((re2[i][0][1], tmp_data_1))
            
                tmp_idx.append(i)
                tmp_i_last = i
                tmp_i_num = tmp
        else:
            tmp_data_1 = interval_statistics(tmp_i_last, i,re2,re3,re4)
            tmp_data.append((re2[i][0][1], tmp_data_1))
            tmp_idx.append(i)

    # 4) insert into db
    if (0 < len(tmp_data)):
        # print tmp_data[0]
        insert_sqlite(tmp_data, symbol, re2[0][0][0])



#######################################################################

for datestr in datestrs:
    logFile = open(ABS_DIR + datestr + "\\log.txt", 'r')

    # 1) logfile
    sqlite_logger.debug("Start to scan records on %s..." % datestr)
    scanErrorFile.write("Start to scan records on %s...\n" % datestr)
    lines = logFile.readlines()
    for line in lines:
        rets = p_jztlog.match(line)
        if (None == rets):
            scanErrorFile.write(line)
            continue
        rets = rets.groups()
        # print(rets)
        list_log.append(rets)


    # 2) scan dirs and insert onemin
    p_tmp1 = re.compile("[a-zA-Z]+")
    p_tmp2 = re.compile("([a-zA-Z]+\d+)\.txt")
    p_tmp3 = re.compile("([a-zA-Z]+\d*)00")

    f_dirs = os.listdir(ABS_DIR + datestr) # 20150430
    for f_dir in f_dirs:
        if (f_dir in exchanges): # SQ
            abs_f_dir = ABS_DIR + datestr + "\\" + f_dir
            abs_f_dir = abs_f_dir.strip()
            sqlite_logger.debug( abs_f_dir)  # E:\dataTickCmmdt\20150430\DQ
            tmp_files = os.listdir(abs_f_dir)
            sqlite_logger.debug( tmp_files )# ['AX', 'AY', 'B', 'BB', 'C',...]

            for tmp_file in tmp_files:
                if (None != p_tmp1.match(tmp_file)):
                    list_sectors.append({'ex':f_dir, 'sector':tmp_file})
                    abs_f_dir_1 = abs_f_dir+"\\"+tmp_file
                    sqlite_logger.debug( abs_f_dir_1)  # E:\dataTickCmmdt\20150430\DQ\AX
                    tmp_files_1 = os.listdir(abs_f_dir_1)
                    for tmp_file_1 in tmp_files_1: # cu00.txt,al00.txt,...
                        tmp_file_1_regex = p_tmp2.match(tmp_file_1)
                        if (None != tmp_file_1_regex):
                            tmp_file_1_regex = tmp_file_1_regex.groups()       
                            sqlite_logger.debug( tmp_file_1_regex) # ('AX00',)
                            list_symbols.append({'sector':tmp_file,'symbol':tmp_file_1_regex})
                            scan_insert(abs_f_dir_1, tmp_file_1, tmp_file_1_regex[0])
    

    # 3) insert other info
    for sec in list_sectors:
        try:
            sqlite_cursor.execute(sql_jzt_tSectors_insert,(sec['sector'],sec['ex']) )
        except sqlite3.Error as err:
            continue
        sqlite_logger.info("Insertion into sectors:%(sec)s,%(ex)s" % {'sec':sec['sector'], 'ex':sec['ex']})
    sqlite_conn.commit()

    for sym in list_symbols:
        try:
            sqlite_cursor.execute(sql_jzt_tContracts_insert,(sym['symbol'][0],sym['sector']) )
        except sqlite3.Error as err:
            sqlite_logger.error("contracts insertion failed, ret = %s" % err.args[0])
            continue
        sqlite_logger.info("Insertion into contracts:%(sym)s,%(sec)s" % {'sym':sym['symbol'],'sec':sym['sector']})
    sqlite_conn.commit()
    
    try:
        sqlite_cursor.execute(sql_jzt_tTradingday_insert,(string.atoi(datestr),))
    except sqlite3.Error as err:
        tmp = string.atoi(datestr) 
        sqlite_logger.error("Insertion into tradingday failed,%i." % tmp)

    sqlite_conn.commit()
    sqlite_logger.debug("Finish to scan records on %s..." % datestr)
    scanErrorFile.write("Finish to scan records on %s...\n" % datestr)

    # 4) list_continuous 
    try:
        sqlite_cursor.execute(sql_jzt_continu_select,(datestr,220))
    except sqlite3.Error as err:
        sqlite_logger.error("select continuous contracts failed:%s" % err.args[0])
    # list_continuous = ["AU30","AU31","AU32","AU33","AU34","AU35"]
    list_continuous = sqlite_cursor.fetchall()
    if (None == list_continuous):
        sqlite_logger.error("continuous is empty.return.")
        # return
    len_continu = len(list_continuous)

    # try:
    #     sqlite_cursor.execute(sql_jzt_continu_select_len,(datestr,))
    # except sqlite3.Error as err:
    #     sqlite_logger.error("select continuous contracts' updatetime failed:%s" % err.args[0])
  

    len_continu_row = 228

    list_continu_data = np.zeros((len_continu_row,4),dtype='f8')
    # array_continu = np.zeros((len_continu_row,len_continu),dtype='f8')
    list_continu_re1 = np.zeros((len_continu,3),dtype='f8')



    # 5) summing up
    tmp_cnt_col = 0
    for continu in list_continuous:
        continu = my_str(continu)
        sqlite_cursor.execute(sql_jzt_continu,(datestr,continu))
        rows = sqlite_cursor.fetchall()
        # if (len_continu_row != len(rows)):
        #     print "wrong rows!%s" % continu
        #     tmp_cnt_col = tmp_cnt_col + 1
        #     continue
        print("%(con)s : %(len)i" % {'con':str(continu),'len':len(rows)})
        list_continu_data = np.zeros((len(rows),4))
        tmp_cnt_row = 0
        for row in rows:
            for i in xrange(4):
                list_continu_data[tmp_cnt_row,i] = row[i]
                # array_continu[tmp_cnt_row,tmp_cnt_col] = row[0]
            tmp_cnt_row = tmp_cnt_row + 1
        tmp_a = trinity(list_continu_data)
        print tmp_a
        list_continu_re1[tmp_cnt_col,0] = tmp_a[0]
        list_continu_re1[tmp_cnt_col,1] = tmp_a[1]
        list_continu_re1[tmp_cnt_col,2] = tmp_a[2]
        tmp_cnt_col = tmp_cnt_col + 1

        try:
            sqlite_cursor.execute(sql_jzt_mktvital_insert,(datestr,continu,tmp_a[0],tmp_a[2],tmp_a[1]))
        except sqlite3.Error as err:
            sqlite_logger.error("mktvital insertion failed:%(con)s,%(arg)s" % {'con':continu, 'arg':err.args[0]})
        sqlite_conn.commit()
    # corr_matrix = my_corr_matrix(array_continu)
    # print corr_matrix
    # heatmap(corr_matrix)
    # plt.show()

sqlite_cursor.close()
sqlite_conn.close()
scanErrorFile.close()
sqlite_logger.debug("Finish scan %s" % datestrs[-1])



