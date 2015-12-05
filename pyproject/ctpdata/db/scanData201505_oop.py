#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ASSUMED that OHLCVAO is cal from beginning of the day: vol starts from 0
# PLS consider if full_len(220) can be divided by resample_len(2), during calc CONTINU


## scan data
import string
import numpy as np
import datetime as dtime

# from utility import timeFil
from utility import sql_jzt_tSectors_insert
from utility import sql_jzt_tContracts_insert
from utility import sql_jzt_tTradingday_insert
from utility import sql_jzt_main 
# from utility import sql_jzt_main_ye 
from utility import sql_jzt_main_select
from utility import trinity
from utility import sql_jzt_continu_select
from utility import sql_jzt_continu_select_2
from utility import sql_jzt_mktvital_insert
# from utility import sql_jzt_mktvital_insert_ye
from utility import sql_jzt_continu_determine_len

from utility import scan_regex_append_errorfile
from utility import fetch_append 
# from utility import interval_statistics
from utility import resample_jzt
# from utility import insert_sqlite
from utility import selectdate_resample

from utility import generate_x_y
from utility import heatmap
from utility import my_corr_matrix
from utility import my_str
import matplotlib.pyplot as plt



import os
import sqlite3
import logging
from patterns import p_jztlog
from patterns import p_jzt
from patterns import p_jzt_tmp1
from patterns import p_jzt_tmp2
from patterns import p_jzt_tmp3

def datestradj_0(list_0):
    y = list_0[2]
    m = list_0[3]
    d = list_0[4]
    tmp_da = len(m)
    if (1 == tmp_da):
        m = '0' + m
    elif (2 != tmp_da):
        print "wrong month is %s" % m
        return

    tmp_db = len(d) 
    if (1 == tmp_db):
        d = '0' + d
    elif (2 != tmp_db):
        print "wrong day is %s" % d
        return

    return y + m + d

class scanner(object):    
    def initList(selg):
        elf.list_log = []
        self.list_sectors = []
        self.list_symbols = [] 
        self.list_continuous = [] #["AU30","AU31","AU32","AU33","AU34","AU35"] 
        self.list_main = [] 

    def __init__(self, datestrs0, onlyIndex=False):
        self.continu_sample_interval = 2
        self.corr_t1 = 132000
        self.corr_t2 = 1530
        self.corr_t3 = 185000  
        # self.corr_y1 = 25000
        self.corr_y2 = 32000
        # self.corr_y3 = 45000
        # self.corr_y4 = 62000
        self.corr_y2_len = 118
        self.corr_y2_list = []
        self.corr_y2_array_len = 60
        # self.corr_y2_array_re


        self.__exchanges = ("DQ","SQ","ZQ","ZJ")        
        self.__datestrs = datestrs0
        FORMAT = '%(asctime)-15s - %(levelname)-6s - %(message)s'
        logging.basicConfig(filename='test_jzt_oop.log', format=FORMAT, level=logging.DEBUG)
        self.__sqlite_logger = logging.getLogger('test')        
        self.__ABS_DIR = "C:\\dataTickCmmdt\\"
        DB_SQLITE_PATH = "C:\\data\\jzt_onemin_oop.db"
        try:
            self.__sqlite_conn = sqlite3.connect(DB_SQLITE_PATH)
        except sqlite3.Error as err:
            print "connection failed."
            self.__sqlite_logger.error("conn. failed, ret = %s" % err.args[0])
            return
        self.__sqlite_cursor = self.__sqlite_conn.cursor()
        
        self.__errorFileStr = "error_jzt_oop.txt"
        self.__scanErrorFile = open(self.__errorFileStr, 'a')

        self.determin_continu_len()
        print self.len_continu_row_full # 198        
        self.len_continu_row_full = 194 
        self.len_continu_row = self.len_continu_row_full / self.continu_sample_interval
        self.len_continu_row = 98 # 198/2

        self.initList() 
        # self.array_continu # panel data
        # self.array_main_re # mktvital
        # self.__re2 
        # self.__re3
        # self.__re4

        if (onlyIndex):
            self.list_continuous = ["AU30","AU31","AU32","AU33","AU34","AU35"]
            len_continu = len(self.list_continuous)
            # list_continu_data = np.zeros((self.len_continu_row,4),dtype='f8')
            self.array_continu = np.zeros((self.len_continu_row, len_continu),dtype='f8')
            self.array_main_re = np.zeros((len_continu,3),dtype='f8')


    def determin_continu_len(self):
        # determine the # of continu
        tmp_d_c_0 = (self.corr_t1, self.corr_t2, self.corr_t3)
        try:
            self.__sqlite_cursor.execute(sql_jzt_continu_determine_len,tmp_d_c_0) 
        except sqlite3.Error as err:
            self.__sqlite_logger.error("failed to determine continu length.return.%s" % err.args[0])
            return
        tmp_d_c = self.__sqlite_cursor.fetchall()
        if (None == tmp_d_c):
            self.__sqlite_logger.error("failed to fetch continu length.return")
            return
        self.len_continu_row_full = tmp_d_c[0][0]
        

    def __insert_sqlite(self,list_data, symbol, date):
        sql_insertion = """insert into `oneminute` (tradingday,updatetime,instrumentid,open,high,low,close,volume,amount,openint) values (?,?,?,?,?,?,?,?,?,?); """
        for data in list_data:        
            try:        
                self.__sqlite_cursor.execute(sql_insertion, (date,data[0],symbol,data[1][0],data[1][1],data[1][2],data[1][3],data[1][4],data[1][5],data[1][6]))
            except sqlite3.Error as err: 
#                self.__sqlite_logger.info("Failed insertion, ret = %(ret)s,symbol:%(symbol)s,dtime:%(date)i,%(time)i " % {'ret':err.args[0],'symbol':symbol,'date':date,'time':data[0]})
                continue

        self.__sqlite_conn.commit()
        

    def __scan_insert(self,absdir, file, symbol):
        # params: (E:\dataTickCmmdt\20150430\DQ\AX, AX00.txt, AX00) 
        # 1) scan ticks
        absfile = absdir + "\\" + file
        ree = []
        scan_regex_append_errorfile(absfile,p_jzt, ree, self.__scanErrorFile)
        ## re2 = np.zeros((len(ree),1), dtype=('a8,i4,f8,i4,f8,i4,f8,i4,f8,i4'))
        ## re2 = np.zeros((len(ree),1), dtype='datetime64')
        self.__re2 = np.zeros((len(ree),1), dtype=('i4,i4'))
        self.__re3 = np.zeros((len(ree),1), dtype = ('f8'))#last
        self.__re4 = np.zeros((len(ree),4), dtype = ('i4'))#v,a,o,b_or_a_inited

        for i in xrange(len(ree)):
            self.__re2[i,0][0] = string.atoi(ree[i][0])*10000 + string.atoi(ree[i][1])*100 + string.atoi(ree[i][2])
            self.__re2[i,0][1] = string.atoi(ree[i][3])*10000 + string.atoi(ree[i][4])*100 + string.atoi(ree[i][5])
            ## re2[i] = np.datetime64(ree[i][0]+'-'+timeFill(ree[i][1])+'-'+timeFill(ree[i][2])+'T'+timeFill(ree[i][3])+':'+ree[i][4]+':'+ree[i][5])
            ## re2[i] = dtime.datetime(string.atoi(ree[i][0]),string.atoi(ree[i][1]),string.atoi(ree[i][2]),string.atoi(ree[i][3]),string.atoi(ree[i][4]),string.atoi(ree[i][5]))
            self.__re3[i] = string.atof(ree[i][6])
            self.__re4[i,0] = string.atoi(ree[i][7])
            self.__re4[i,1] = string.atoi(ree[i][8])
            self.__re4[i,2] = string.atoi(ree[i][9])
            self.__re4[i,3] = string.atoi(ree[i][10])
    
        # 2) aggregation, one min
        tmp_idx = []
        tmp_data = []
        resample_jzt(self.__re2,self.__re3,self.__re4,self.__sqlite_logger,1,tmp_data,tmp_idx)
    
        # 3) insert into db
        if (0 < len(tmp_data)):
            # print tmp_data[0]
            self.__insert_sqlite(tmp_data, symbol, self.__re2[0][0][0])


    def __1_logfile(self,datestr):
        logFile = open(self.__ABS_DIR + datestr + "\\log.txt", 'r')
        self.__sqlite_logger.debug("Start to scan records on %s..." % datestr)
        self.__scanErrorFile.write("Start to scan records on %s...\n" % datestr)
        tmp_1_1 = self.__ABS_DIR + datestr + "\\log.txt"
        scan_regex_append_errorfile(tmp_1_1,p_jztlog,self.list_log,self.__scanErrorFile)

    def __2_scan_insert_onemin(self,datestr):
        f_dirs = os.listdir(self.__ABS_DIR + datestr) # 20150430
        for f_dir in f_dirs:
            if (f_dir in self.__exchanges): # SQ
                abs_f_dir = self.__ABS_DIR + datestr + "\\" + f_dir
                abs_f_dir = abs_f_dir.strip()
                self.__sqlite_logger.debug( abs_f_dir)  # E:\dataTickCmmdt\20150430\DQ
                tmp_files = os.listdir(abs_f_dir)
                self.__sqlite_logger.debug( tmp_files )# ['AX', 'AY', 'B', 'BB', 'C',...]
                
                for tmp_file in tmp_files:
                    if (None != p_jzt_tmp1.match(tmp_file)):
                        self.list_sectors.append({'ex':f_dir, 'sector':tmp_file})
                        abs_f_dir_1 = abs_f_dir+"\\"+tmp_file  # E:\dataTickCmmdt\20150430\DQ\AX
                        self.__sqlite_logger.debug( abs_f_dir_1)  
                        tmp_files_1 = os.listdir(abs_f_dir_1)
                        for tmp_file_1 in tmp_files_1: # AX00.txt,AX01.txt,...
                            tmp_file_1_regex = p_jzt_tmp2.match(tmp_file_1)
                            if (None != tmp_file_1_regex):
                                tmp_file_1_regex = tmp_file_1_regex.groups()       
                                self.__sqlite_logger.debug( tmp_file_1_regex) # ('AX00',)
                                self.list_symbols.append({'sector':tmp_file,'symbol':tmp_file_1_regex})
                                self.__scan_insert(abs_f_dir_1, tmp_file_1, tmp_file_1_regex[0]) # (E:\dataTickCmmdt\20150430\DQ\AX, AX00.txt, AX00) 
                                
    def __3_insert_otherinfo(self,datestr):
        for sec in self.list_sectors:
            try:
                self.__sqlite_cursor.execute(sql_jzt_tSectors_insert,(sec['sector'],sec['ex']) )
            except sqlite3.Error as err:
                continue
            self.__sqlite_logger.info("Insertion into sectors:%(sec)s,%(ex)s" % {'sec':sec['sector'], 'ex':sec['ex']})
        self.__sqlite_conn.commit()

        for sym in self.list_symbols:
            try:
                self.__sqlite_cursor.execute(sql_jzt_tContracts_insert,(sym['symbol'][0],sym['sector']) )
            except sqlite3.Error as err:
                # self.__sqlite_logger.error("contracts insertion failed, ret = %s" % err.args[0])
                continue
            self.__sqlite_logger.info("Insertion into contracts:%(sym)s,%(sec)s" % {'sym':sym['symbol'],'sec':sym['sector']})
        self.__sqlite_conn.commit()
    
        tmp_3_str = string.atoi(datestr)
        try:
            self.__sqlite_cursor.execute(sql_jzt_tTradingday_insert,(tmp_3_str,))
        except sqlite3.Error as err:
            self.__sqlite_logger.error("Insertion into tradingday failed,%(i)i, :%(s)s" % {'i':tmp_3_str,'s':err.args[0]})

        self.__sqlite_conn.commit()
        self.__sqlite_logger.debug("Finish to scan records on %s..." % datestr)
        self.__scanErrorFile.write("Finish to scan records on %s...\n" % datestr)
        

    def __4_list_continuous(self,datestr):
        tmp_4_0 = tuple()
        fetch_append(sql_jzt_main_select,self.__sqlite_cursor,self.__sqlite_logger,self.list_main,"select main contracts failed",tmp_4_0)
        if (0 >= len(self.list_main)):
            return
        self.array_main_re = np.zeros((len(self.list_main), 3),dtype='f8')

        tmp_4_2 = (datestr,self.corr_t1,self.corr_t2,self.corr_t3,self.len_continu_row_full) # 212
        fetch_append(sql_jzt_continu_select,self.__sqlite_cursor,self.__sqlite_logger,self.list_continuous,"select continuous contracts failed",tmp_4_2) 
        if (len(self.list_continuous) > 0):
            len_continu = len(self.list_continuous) # 26
            self.array_continu = np.zeros((self.len_continu_row, len_continu),dtype='f8') # 220/2,26
        else:
            self.__sqlite_logger.error("Failed to find any continuous contracts.")

        ## night shift 
        tmp_4_3 = (datestr,12000,self.corr_y2,self.corr_y2_len)
        fetch_append(sql_jzt_continu_select_2,self.__sqlite_cursor,self.__sqlite_logger,self.corr_y2_list,"select y2 failed.",tmp_4_3)
        tmp_4_4 = len(self.corr_y2_list)
        if (0 >= tmp_4_4):
            self.__sqlite_logger.error("Failed to find y2 contracts.")
        else:
            self.corr_y2_array_re = np.zeros((self.corr_y2_array_len, tmp_4_4),dtype='f8')
        

    def __sum_main(self,datestr,list,sql_select,argss,min_count,array_re, sql_insert):
        tmp_cnt_col = 0
        for mn in list:
            tmp = []
            tmp.append(datestr)
            tmp.append(mn)
            for i in xrange(len(argss)):
                tmp.append(argss[i])
            tmp_1 = tuple(tmp)
            self.__sqlite_cursor.execute(sql_select, tmp_1)
            rows = self.__sqlite_cursor.fetchall()
            if (min_count >= len(rows)):
                self.__sqlite_logger.error("%(a)s:less than %(b)i data!continue." % {'a':mn,'b':min_count})
                tmp_cnt_col = tmp_cnt_col + 1
                continue
            self.__sqlite_logger.debug("%(con)s : %(len)i" % {'con':str(mn),'len':len(rows)})

            ## assign list to np.array
            list_data = np.array(rows)
            tmp_a = trinity(list_data) # mktvital4datestr
            for i in xrange(3):
                array_re[tmp_cnt_col,i] = tmp_a[i]
            tmp_cnt_col = tmp_cnt_col + 1
            
            try:
                self.__sqlite_cursor.execute(sql_insert,(datestr,mn,tmp_a[0],tmp_a[2],tmp_a[1]))
            except sqlite3.Error as err:
                self.__sqlite_logger.error("mktvital might shift insertion failed:%(con)s,%(arg)s" % {'con':mn, 'arg':err.args[0]})

        self.__sqlite_conn.commit()   


    def __5_sumup_main(self,datestr):
        self.__sum_main(datestr,self.list_main,sql_jzt_main,tuple(),100,self.array_main_re, sql_jzt_mktvital_insert)

        # tmp_cnt_col = 0        
        # for mn in self.list_main:
        #     # print((datestr,mn))
        #     self.__sqlite_cursor.execute(sql_jzt_main,(datestr,mn))
        #     rows = self.__sqlite_cursor.fetchall() # mkt4datestr
        #     if (100 >= len(rows)):
        #         self.__sqlite_logger.error("%s: less than 100 data!return!" % mn)
        #         tmp_cnt_col = tmp_cnt_col + 1
        #         continue
        #     self.__sqlite_logger.debug("%(con)s : %(len)i" % {'con':str(mn),'len':len(rows)})

        #     ## assign list to np.array
        #     list_data = np.array(rows)
        #     tmp_a = trinity(list_data) # mktvital4datestr

        #     self.array_main_re[tmp_cnt_col,0] = tmp_a[0]
        #     self.array_main_re[tmp_cnt_col,1] = tmp_a[1]
        #     self.array_main_re[tmp_cnt_col,2] = tmp_a[2]
        #     tmp_cnt_col = tmp_cnt_col + 1 # BLANK may exists in self.array_main_re, but not in db

        #     try:
        #         self.__sqlite_cursor.execute(sql_jzt_mktvital_insert,(datestr,mn,tmp_a[0],tmp_a[2],tmp_a[1]))
        #     except sqlite3.Error as err:
        #         self.__sqlite_logger.error("mktvital insertion failed:%(con)s,%(arg)s" % {'con':mn, 'arg':err.args[0]})

        # self.__sqlite_conn.commit()   

    def __sum_continu(self,datestr,freq): 
        datenum = int(datestr)
        # freq = int(self.continu_sample_interval)
        if (freq <= 0):
            print("wrong resampling frequency!return!")
            return

        tmp_6_1 = int(self.corr_t1/100)
        tmp_6_2 = int(self.corr_t3/100)
        tmp_6_5 = []
        for i in xrange(len(self.list_continuous)):
            tmp_6_name = self.list_continuous[i]
            re_d,re_OHLC,re_VAO = selectdate_resample(tmp_6_name,datenum,datenum,self.continu_sample_interval,self.__sqlite_conn,self.__sqlite_cursor)
            
            tmp_6 = []
            for j in xrange(len(re_d)):
                tmp_6_0 = re_d[j][1]
                if (tmp_6_1 < tmp_6_0 and self.corr_t2 != tmp_6_0 and tmp_6_2 >= tmp_6_0):
                    tmp_6.append(j)

            print "%(a)s %(b)i" % {'a':tmp_6_name,'b':len(tmp_6)}
            if (self.len_continu_row == len(tmp_6)):
                self.array_continu[:,i] = re_OHLC[tmp_6,3]
                tmp_6_5.append(i)
            else:
                self.__sqlite_logger.debug("%(a)s %(b)i" % {'a':datestr,'b':len(tmp_6)})
                                         
        if (0 < len(tmp_6_5)):
#            self.array_continu = self.array_continu[tmp_6_5,tmp_6_5]
            tmp_6_4 = np.shape(self.array_continu);
            tmp_6_array = np.zeros((tmp_6_4[0],len(tmp_6_5)))
            for ii in xrange(len(tmp_6_5)):
                tmp_6_array[:,ii] = self.array_continu[:,tmp_6_5[ii]] 
                
            self.array_continu_re = my_corr_matrix(tmp_6_array)
            heatmap(self.array_continu_re)
            plt.show()

            sqls_6 = """
            insert into realizedcorr 
            values (?,?,?,?,0,datetime())
            """
            for i in xrange(len(self.array_continu_re)):
                for j in xrange(i):
                    tmp_6_3 = (string.atoi(datestr),self.list_continuous[j],self.list_continuous[i],self.array_continu_re[j,i])
                    try:
                        self.__sqlite_cursor.execute(sqls_6, tmp_6_3)
                    except sqlite3.Error as err:
                        self.__sqlite_logger.error("Failed insertion into corr:%(a)s,%(b)s.RET:%(c)s" % {'a':self.list_continuous[j],'b':self.list_continuous[i],'c':err.args[0]})
                          
            self.__sqlite_conn.commit() 


    def __6_sumup_continu(self, datestr):
        datenum = int(datestr)
        freq = int(self.continu_sample_interval)
        if (freq <= 0):
            print("wrong resampling frequency!return!")
            return

        tmp_6_1 = int(self.corr_t1/100)
        tmp_6_2 = int(self.corr_t3/100)
        tmp_6_5 = []
        for i in xrange(len(self.list_continuous)):
            tmp_6_name = self.list_continuous[i]
            re_d,re_OHLC,re_VAO = selectdate_resample(tmp_6_name,datenum,datenum,self.continu_sample_interval,self.__sqlite_conn,self.__sqlite_cursor)
            
            tmp_6 = []
            for j in xrange(len(re_d)):
                tmp_6_0 = re_d[j][1]
                if (tmp_6_1 < tmp_6_0 and self.corr_t2 != tmp_6_0 and tmp_6_2 >= tmp_6_0):
                    tmp_6.append(j)

            print "%(a)s %(b)i" % {'a':tmp_6_name,'b':len(tmp_6)}
            if (self.len_continu_row == len(tmp_6)):
                self.array_continu[:,i] = re_OHLC[tmp_6,3]
                tmp_6_5.append(i)
            else:
                self.__sqlite_logger.debug("%(a)s %(b)i" % {'a':datestr,'b':len(tmp_6)})
                                         
        if (0 < len(tmp_6_5)):
#            self.array_continu = self.array_continu[tmp_6_5,tmp_6_5]
            tmp_6_4 = np.shape(self.array_continu);
            tmp_6_array = np.zeros((tmp_6_4[0],len(tmp_6_5)))
            for ii in xrange(len(tmp_6_5)):
                tmp_6_array[:,ii] = self.array_continu[:,tmp_6_5[ii]] 
                
            self.array_continu_re = my_corr_matrix(tmp_6_array)
            heatmap(self.array_continu_re)
            plt.show()

            sqls_6 = """
            insert into realizedcorr 
            values (?,?,?,?,0,datetime())
            """
            for i in xrange(len(self.array_continu_re)):
                for j in xrange(i):
                    tmp_6_3 = (string.atoi(datestr),self.list_continuous[j],self.list_continuous[i],self.array_continu_re[j,i])
                    try:
                        self.__sqlite_cursor.execute(sqls_6, tmp_6_3)
                    except sqlite3.Error as err:
                        self.__sqlite_logger.error("Failed insertion into corr:%(a)s,%(b)s.RET:%(c)s" % {'a':self.list_continuous[j],'b':self.list_continuous[i],'c':err.args[0]})
                          
            self.__sqlite_conn.commit()        
                
    # def __del__(self):
    def __cleanup(self):
        self.__sqlite_cursor.close()
        self.__sqlite_conn.close()
        self.__scanErrorFile.close()
        self.__sqlite_logger.debug("Finish scan %s" % self.__datestrs[-1])

    def datestradj(self):
        if (len(self.list_log) <= 0):
            print "empty list_log.return"
            return
        tmp_da_1 = datestradj_0(self.list_log[0])
        for i in range(1, len(self.list_log)):
            tmp_da_2 = datestradj_0(self.list_log[i])
            if (tmp_da_1 != tmp_da_2):
                print "different datestr %(1)s:%(2)s.return" % {'1':tmp_da_1,'2':tmp_da_2}
                return

        return tmp_da_1

    def process(self):
        for datestr in self.__datestrs:
            self.__1_logfile(datestr)
            datestr_adjusted = self.datestradj()
            self.__2_scan_insert_onemin(datestr_adjusted)
            self.__3_insert_otherinfo(datestr_adjusted)
            self.__4_list_continuous(datestr_adjusted)
            self.__5_sumup_main(datestr_adjusted)
            self.__6_sumup_continu(datestr_adjusted)
            self.initList()  
        self.__cleanup()    


                

# a=scanner(["20150518"])
# a=scanner(["20150519"])
# a=scanner(["20150521"])
# a=scanner(["20150522"])
# a = scanner(["20150525"])
# a = scanner(["20150526"])
# a = scanner(["20150527"])
# a = scanner(["20150528"])
a = scanner(["20150529"])
a.process()
