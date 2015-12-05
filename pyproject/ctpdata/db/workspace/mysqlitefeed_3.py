#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import logging
# import string
# import numpy as np
import datetime as dtime

from pyalgotrade import bar
# from pyalgotrade.barfeed import sqlitefeed
from pyalgotrade.barfeed import membf
from pyalgotrade import dataseries
from mybasicbar import myBasicBar

DB_SQLITE_PATH = "/home/dell/data/jzt/pyalgo_1min.db"
DB_ORIGIN = "/home/dell/data/jzt/jzt_onemin_oop_2.db"
FORMAT = '%(asctime)-15s - %(levelname)-6s - %(message)s'
logging.basicConfig(filename='mysqlitefeed.log', format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger("sqlitefeed")


def normalize_instrument(instrument):
    return instrument.upper()

def tri_poly(int_num):
    int_num = int(int_num)
    tmp1 = (int_num / 10000)
    tmp2 = ((int_num - tmp1*10000)/100)
    tmp3 = int_num - tmp1*10000 - tmp2*100
    return([tmp1,tmp2,tmp3])

def formdatetime(idate,itime):
    tmp1,tmp2,tmp3 = tri_poly(idate)
    # tmp4,tmp5,tmp6 = tri_poly(string.atoi(timestr))
    tmp4,tmp5,tmp6 = tri_poly(itime)
    return dtime.datetime(tmp1,tmp2,tmp3,tmp4,tmp5) # only accu. w.r.t minute BY FAR.

def formdatetime_60(idate, tmp4, tmp5):
## form oneminute bar
    idate1 = tri_poly(idate)
    try:
        # print("%s %i %i %i %i %i\n" % (type(tmp4),idate1[0],idate1[1],idate1[2],tmp4,tmp5))
        tmp6 = dtime.datetime(idate1[0],idate1[1],idate1[2],tmp4,tmp5) # only accu. w.r.t minute BY FAR.
    except ValueError as e: 
        logger.error("formdatetime_60 failed: ValueError|%s|%s." % (''.join((str(idate), ':',str(tmp4*100+tmp5))), e.args[0]))
        return
    except Exception as e:
        logger.error("formdatetime_60 failed: Exception|%s|%s." % (''.join((str(idate), ':',str(tmp4*100+tmp5))), e.args[0]))
        return
    # else:
    #     logger.error("formdatetime_60 failed")
    #     return 
    return(tmp6)

def formatbasicbar_60(x):
# tradingday,updatetime,open,high,low,close,volume,openint,sgnvol
    try:
        tmp = x[1].strip().split(':')
        tmp0 = formdatetime_60(x[0], int(tmp[0]), int(tmp[1]))
        # tmp1 = dtime.datetime(tmp0[0],tmp0[1],tmp0[2],tmp0[3],tmp0[4])
        if (tmp0 is not None):
            re = myBasicBar(tmp0,x[2],x[3],x[4],x[5],x[6],x[7],x[8])
        else:
            return
    except Exception as e:
        logger.error("formatbasicbar_60 failed|%s" % e.args[0])
        return
    return re


def formatbasicbar_day(x):
# tradingday,open,high,low,close,volume,openint
    try:
        tmp0 = tri_poly(x[0])
        if (tmp0 is not None):
            re = myBasicBar(tmp0,x[1],x[2],x[3],x[4],x[5],x[6], None, 86400)
        else:
            return
    except Exception as e:
        logger.error("formatbasicbar_day failed|%s" % e.args[0])
        return
    return re


class mysqlitefeed(membf.BarFeed):
    def __init__(self,dbFilePath, frequency, maxLen=dataseries.DEFAULT_MAX_LEN):
        membf.BarFeed.__init__(self,frequency,maxLen)
        self.connect(dbFilePath)
        # self.dates = dates
        # self.instrumentids = instruments

    def connect(self, dbFilePath):
        try:
            self.__conn = sqlite3.connect(dbFilePath)
        except sqlite3.Error as err:
            logger.error("connection failed:%s" % err.args[0])
            return
        except Exception as e:
            logger.error("connection failed|%s" % e.args[0])
            return
        # self.__conn.isolation_level = None  # To do auto-commit
        ## SHOULD NOT change the database!!!
        try:
            self.__cur = self.__conn.cursor()
        except Exception as e:
            logger.error("Failed cursor|%s" % e.args[0])
            return
        # self.__db = self.myfeed.getDatabase()
        return True

    def loadBars(self, instrument, fromDateTime=None, toDateTime=None, timezone=None):
        instrument = normalize_instrument(instrument)
        tmp = self.__fetchdata(instrument, self.getFrequency(), fromDateTime, toDateTime, timezone)
        if (tmp is not None):
            if (60 == self.getFrequency()):
                bars = map(formatbasicbar_60, tmp)
            elif (60*60*24 == self.getFrequency()):
                bars = map(formatbasicbar_day, tmp)
            else:
                logger.error("Only minute and day freq. can be processed.return.")
            self.addBarsFromSequence(instrument, bars)
        

    def __fetchdata(self,instrument,frequency,fromm,too,tzone):
        if (frequency == 60):
            sqls = "select tradingday,updatetime,open,high,low,close,volume,openint,sgnvol from oneminute where instrumentid = ? "
            args = [instrument]
            if fromm is not None:
                ## only data in days
                sqls += " and tradingday >= ?"
                args.append(fromm)
            if too is not None:
                sqls += " and tradingday <= ?"
                args.append(too)
            sqls += " order by tradingday ASC, updatetime ASC;"
        elif (frequency == 24*60*60):
            sqls = "select tradingday,open,high,low,close,volume,openint from day where instrumentid = ? "
            args = [instrument]
            if fromm is not None:
                ## only data in days
                sqls += " and tradingday >= ?"
                args.append(fromm)
            if too is not None:
                sqls += " and tradingday <= ?"
                args.append(too)
            sqls += " order by tradingday ASC;"
        else:
            return

        try:
            self.__cur.execute(sqls, args)
        except sqlite3.Error as err:
            logger.error("failed to select:%(a)s %(b)s %(c)s" % {'a':instrument,'b':fromm,'c':err.args[0]})

        rows = self.__cur.fetchall()
        if (None == rows):
            self.logger.error("failed to fetch:%(a)s %(b)s %(c)s" % {'a':instrument, 'b':fromm,'c':err.args[0]})
            return
        # print id(rows)
        return rows

    # def addBars(self,instrumentid,datee):
    #     tmps = self.fetchdata(instrumentid,datee)            
    #     for tmp in tmps:
    #         tmp_a1 = formdatetime(datee, tmp[0])
    #         try:
    #             tmp_aBar = bar.BasicBar(tmp_a1,tmp[2],tmp[3],tmp[4],tmp[5],tmp[6],tmp[7],60)
    #         except sqlite3.Error as err:
    #             self.logger.info("failed to form bar:%(a)i,%(b)i,%(c)i,%(d)i,%(e)i,%(f)i,%(g)i." % {'a':datee,'b':tmp[2],'c':tmp[3],'d':tmp[4],'e':tmp[5],'f':tmp[6],'g':tmp[7]})
    #         self.db.addBar(instrumentid,tmp_aBar,60)

    def closeup(self):
        self.__cur.close()
        self.__cur = None
        self.__conn.close()
        self.__conn = None
        # self.db.disconnect()

    def barsHaveAdjClose(self):
        return False
        
    # def process(self):
    #     self.__connect()
    #     for datee in self.dates:
    #         tmp_pdate = string.atoi(datee)
    #         for instrumentid in self.instrumentids:
    #             self.logger.debug("date:%(a)i,instrument:%(b)s : starts recording." % {'a':tmp_pdate,'b':instrumentid})
    #             self.addBars(instrumentid, tmp_pdate)
                
    #     self.closeup()
    #     self.logger.debug("Finished.")




# # a = mysqlitefeed(["20150521","20150522"],["IF00"])            
# # a = mysqlitefeed(["20150521","20150522"],["IH00","IC00"])
# # list_date = ["20150525","20150526","20150527","20150528","20150529","20150601","20150602","20150603","20150604","20150605"]
# # list_symbol = ["IF00","IH00","IC00"]
# # list_date = ["20150521","20150522","20150525","20150526","20150527","20150528","20150529","20150601","20150602","20150603","20150604","20150605"]
# list_symbol = ["AG00","AX00","CF00","CU00","FG00","I00","J00","JD00","JM00","L00","M00","MA00","NI00","P00","PP00","RB00","RM00","RU00","SRX00","TA00","TC00","AU00","C00","OI00","Y00"]
# # list_date = ["20150711","20150713","20150714"]
# list_date = ["20150715","20150716","20150717","20150720","20150721","20150722","20150723","20150724"]


# a = mysqlitefeed(list_date, list_symbol)
# a.process()


# # fd = sqlitefeed.Feed(DB_SQLITE_PATH, 60)
# # # fd.loadBars("IF00")
# # # fd.loadBars("IC00",None,dtime.datetime(2015,5,21,7),dtime.datetime(2015,5,23))
# # from test0 import MyStrategy
# # myStrategy = MyStrategy(fd, "IF00")
# # myStrategy.run()






