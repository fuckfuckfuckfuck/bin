
# -*- coding: utf-8 -*-

import sqlite3
import logging
import string
import numpy as np
import datetime as dtime

from pyalgotrade import bar
from pyalgotrade.barfeed import sqlitefeed
DB_SQLITE_PATH = "/home/dell/data/jzt/pyalgo_1min.db"
DB_ORIGIN = "/home/dell/data/jzt/jzt_onemin_oop.db"


def tri_poly(int_num):
    tmp1 = int(int_num / 10000)
    tmp2 = int((int_num - tmp1*10000)/100)
    tmp3 = int_num - tmp1*10000 - tmp2*100
    return tmp1,tmp2,tmp3

def formdatetime(idate,itime):
    tmp1,tmp2,tmp3 = tri_poly(idate)
    # tmp4,tmp5,tmp6 = tri_poly(string.atoi(timestr))
    tmp4,tmp5,tmp6 = tri_poly(itime)
    return dtime.datetime(tmp1,tmp2,tmp3,tmp4,tmp5) # only accu. w.r.t minute BY FAR.

class mysqlitefeed(object):
    def __init__(self,dates,instruments):       
        self.myfeed = sqlitefeed.Feed(DB_SQLITE_PATH, 60)
        FORMAT = '%(asctime)-15s - %(levelname)-6s - %(message)s'
        logging.basicConfig(filename='sqlitefeed.log', format=FORMAT, level=logging.DEBUG)
        self.logger = logging.getLogger("sqlitefeed")
        self.dates = dates
        self.instrumentids = instruments

    def __connect(self):
        try:
            self.conn = sqlite3.connect(DB_ORIGIN)
        except sqlite3.Error as err:
            self.logger.error("connection failed:%s" % err.args[0])
            return
        self.cur = self.conn.cursor()
        self.db = self.myfeed.getDatabase()
        
    def fetchdata(self,instrumentid,date):
        sqls = "select updatetime,instrumentid,open,high,low,close,volume,openint from oneminute where tradingday = ? and instrumentid = ? order by updatetime;"
        try:
            self.cur.execute(sqls,(date,instrumentid))
        except sqlite3.Error as err:
            self.logger.error("failed to select:%(a)s %(b)s %(c)s" % {'a':instrumentid,'b':date,'c':err.args[0]})
        rows = self.cur.fetchall()
        if (None == rows):
            self.logger.error("failed to fetch:%(a)s %(b)s %(c)s" % {'a':instrumentid, 'b':date,'c':err.args[0]})
            return
        print id(rows)
        return rows

    def addBars(self,instrumentid,datee):
        tmps = self.fetchdata(instrumentid,datee)            
        for tmp in tmps:
            tmp_a1 = formdatetime(datee, tmp[0])
            try:
                tmp_aBar = bar.BasicBar(tmp_a1,tmp[2],tmp[3],tmp[4],tmp[5],tmp[6],tmp[7],60)
            except sqlite3.Error as err:
                self.logger.info("failed to form bar:%(a)i,%(b)i,%(c)i,%(d)i,%(e)i,%(f)i,%(g)i." % {'a':datee,'b':tmp[2],'c':tmp[3],'d':tmp[4],'e':tmp[5],'f':tmp[6],'g':tmp[7]})
            self.db.addBar(instrumentid,tmp_aBar,60)

    def closeup(self):
        self.cur.close()
        self.conn.close()
        self.db.disconnect()
        
    def process(self):
        self.__connect()
        for datee in self.dates:
            tmp_pdate = string.atoi(datee)
            for instrumentid in self.instrumentids:
                self.logger.debug("date:%(a)i,instrument:%(b)s : starts recording." % {'a':tmp_pdate,'b':instrumentid})
                self.addBars(instrumentid, tmp_pdate)
                
        self.closeup()
        self.logger.debug("Finished.")

# a = mysqlitefeed(["20150521","20150522"],["IF00"])            
# a = mysqlitefeed(["20150521","20150522"],["IH00","IC00"])
# list_date = ["20150525","20150526","20150527","20150528","20150529","20150601","20150602","20150603","20150604","20150605"]
# list_symbol = ["IF00","IH00","IC00"]
# list_date = ["20150521","20150522","20150525","20150526","20150527","20150528","20150529","20150601","20150602","20150603","20150604","20150605"]
# list_symbol = ["AG00","AX00","CF00","CU00","FG00","I00","J00","JD00","JM00","L00","M00","MA00","NI00","P00","PP00","RB00","RM00","RU00","SRX00","TA00","TC00","AU00","C00","OI00","Y00"]


a = mysqlitefeed(list_date, list_symbol)
a.process()


# fd = sqlitefeed.Feed(DB_SQLITE_PATH, 60)
# # fd.loadBars("IF00")
# # fd.loadBars("IC00",None,dtime.datetime(2015,5,21,7),dtime.datetime(2015,5,23))
# from test0 import MyStrategy
# myStrategy = MyStrategy(fd, "IF00")
# myStrategy.run()






