#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
# import logging.config
import sqlite3
import scanCtp
# from scanConf import scanedParams
import time
import sys


# datestrs = ["20150105"]
# datestrs = ["20150703"]
# datestrs = ["20150702"]
# datestrs = ["20150701"]
# datestrs = ["20150630"]
# datestrs = ["20150629"]
# datestrs = ["20150626"]
# datestrs = ["20150625"]
# datestrs = ["20150706"]
# datestrs = ["20150707"]
# datestrs = ["20150708"]
# datestrs = ["20150709"]
# datestrs = ["20150824"]
# datestrs = ["20150825"]
# datestrs = ["20150826"]
# datestrs = ["20150827"]
# datestrs = ["20150828"]
# datestrs = ["20151012"]
datestrs = ["20151109","20151110"]


DB_SQLITE_PATH = "/home/dell/data/ctp_" + datestrs[0] +".db"
ABSOLUTE_DIR = "/home/dell/bin/ctp/test7/7d/"


## twin loggings.
scanErrFile =  open("scanerror.txt",'a')
FORMAT = '%(asctime)-15s - %(levelname)-6s - %(message)s'
logging.basicConfig(filename='test.log', format=FORMAT, level=logging.DEBUG)
sqlite_logger = logging.getLogger('test')


def process():    
## following needs to be simplified.##
##-------------------------------------------------------------------------------------------------------------##
    ##1) connect db
    try:
        sqlite_conn = sqlite3.connect(DB_SQLITE_PATH)
    except sqlite3.Error as err:
        print 'conntect sqlite database failed.'
        sqlite_logger.error("conntect sqlite database failed, ret = %s" % err.args[0])
        return
##2) cursor        
    sqlite_cursor = sqlite_conn.cursor()
##3) detect table
#    sql_desc2 = "DROP TABLE IF EXISTS ?;"
    sql_desc2 = """select count(*) from sqlite_master where type= 'table' and name = 'mktinfo';""";
    sqlite_cursor.execute(sql_desc2)
    row = sqlite_cursor.fetchone()

    if (row is None or row[0] > 0):
        print("table mktinfo already exists. return" )
        sqlite_logger.error("table mktinfo already exists. return")
        return
## delete table    
       # try:
       #      sqlite_cursor.execute(sql_desc2)
       #  except sqlite3.Error as e:
       #      print 'drop table failed'
       #      sqlite_logger.error("drop table failed, ret = %s" % e.args[0])
       #      sqlite_cursor.close()
       #      sqlite_conn.close()     
       #      return
       #  sqlite_conn.commit()       
##4) create table
## //**
    sql_desc = scanCtp.sql_create_table
    try:
        sqlite_cursor.execute(sql_desc)        
    except sqlite3.Error as e:
        print 'create table failed.'
        sqlite_logger.error("create table failed, ret = %s" % e.args[0])
        sqlite_cursor.close()
        sqlite_conn.close()   
        return
    sqlite_conn.commit()
    sqlite_logger.debug("create table( mktinfo ) succ.")
##5)
    for datestr in datestrs:
        insertRecord(datestr, sqlite_conn, sqlite_cursor)
##6) clean up datestr
    sqlite_cursor.close()
    sqlite_conn.close()
    scanErrFile.close()
    sqlite_logger.debug("Finish scan %s" % datestr)    


def insertRecord(datestr, sqlite_conn, sqlite_cursor):    
    sqlite_logger.debug("Start to scan records on %s..." % datestr)
    scanErrFile.write("Start to scan records on %s...\n" % datestr)
    datafile = scanCtp.findTestlogfiles(ABSOLUTE_DIR + datestr)    
## open files
    sql_desc3 = scanCtp.sql_add_record_2
    for i in datafile:
        tmp_name = ABSOLUTE_DIR + datestr +'/'+i
        ifile = open(tmp_name, 'r')
        print tmp_name
        scanErrFile.write("Begin scanning %s \n" % tmp_name)
        sqlite_logger.info("Begin scanning %s " % tmp_name)
        datalines = ifile.readlines()
        for line in datalines:
            # line = "18246655 [139707331954432] DEBUG test <> - 20140627 au1408   263.25 264.05 263.8 212 262.45 263.25 262.45 16 4.2072e+06 220 1.79769e+308 1.79769e+308 277.25 250.8 02:00:15 0 262.75 2 263.3 1 262950 255957"
            re = scanCtp.p.match(line)
            if (re == None):
                scanErrFile.write(line)
                continue
            re = re.groups()
## data constraints
            tmp_list = scanCtp.record_2(re)
## insert records
            try:
                sqlite_cursor.execute(sql_desc3, tmp_list)
            except sqlite3.Error as e:
                print 'insert record failed. %s' % e.args[0]
                sqlite_logger.error("Failed insert,ret=%s" % e.args[0])
                scanErrFile.write(line)
                continue 
## clean up datafile
        sqlite_conn.commit()
        try:
            ifile.read()
        finally:
            ifile.close()
        sqlite_logger.info("Finish scanning %s" % i)


if __name__ == '__main__':
    process();
