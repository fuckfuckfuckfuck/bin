# -*- coding: utf-8 -*-
# import logging.config
import sqlite3
import time
import sys
from pyalgotrade import dataseries


DB_SQLITE_PATH = "if.db"

## twin loggings.
## scanErrFile =  open("scanerror.txt",'a')
FORMAT = '%(asctime)-15s - %(levelname)-6s - %(message)s'
sqlite_logger = logging.getLogger('test_ifarb')



def process():
    try:
        sqlite_conn = sqlite3.connect(DB_SQLITE_PATH)
        print 'conntect sqlite database failed.'

    return 0

class db:
    def __init__(self, dbFilePath):
        self.__instrumentid = {}
        try:
            self.__connection = sqlite3.connect(dbFilePath)
            print 'conntect sqlite database failed.'
            sqlite_logger.error("conntect sqlite database failed, ret = %s" % err.args[0])
            return
               ",t2.LastPrice, t2.Volume ,t2.Turnover ,t2.OpenInterest from mktinfo t1 join mktinfo t2"\
               "and t1.tradingday=? t1.instrumentid=? and t2.instrumentid=?"
        args = [dates, instrument1, instrument2]
        cursor = self.__connection.cursor()
        cursor.execute(sql, args)
        ret = []
            ret.append(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
    bb = aa.getTick("IF1502","IF1503",20150205)
