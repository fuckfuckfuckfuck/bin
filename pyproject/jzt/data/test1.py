#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
# import logging.config
import sqlite3
import scanCtp
import time
import sys

## datestrs = ["20141205","20141204","20141203","20141202","20141201"]
## datestrs = ["20150126","20150126A","20150127","20150128","20150129","20150130"]
## datestrs = ["20150202","20150203"]
datestrs = ["20150205"]
DB_SQLITE_PATH = "ctp_"+datestrs[0]+".db"

scanErrFile =  open("scanerror.txt",'a')
sqlite_logger = logging.getLogger('test')


def process():    
## following needs to be simplified.##
    try:
    except sqlite3.Error as err:
        sqlite_logger.error("conntect sqlite database failed, ret = %s" % err.args[0])
##2) cursor        
    sqlite_cursor = sqlite_conn.cursor()
#    sql_desc2 = "DROP TABLE IF EXISTS ?;"
    sql_desc2 = """select count(*) from sqlite_master where type= 'table' and name = 'mktinfo';""";
    row = sqlite_cursor.fetchone()
    if (row[0] is None or row[0] > 0):
       #      sqlite_cursor.execute(sql_desc2)
       #      print 'drop table failed'
       #      sqlite_logger.error("drop table failed, ret = %s" % e.args[0])
       #      sqlite_cursor.close()
       #      return
##4) create table
## //**
    try:
        sqlite_cursor.execute(sql_desc)        
        sqlite_logger.error("create table failed, ret = %s" % e.args[0])
        return
    sqlite_conn.commit()
    sqlite_logger.debug("create table( mktinfo ) succ.")
##6) clean up datestr
    sqlite_cursor.close()
    sqlite_conn.close()
    scanErrFile.write("Start to scan records on %s...\n" % datestr)
##open files
    sql_desc3 = scanCtp.sql_add_record_2
    for i in datafile:
            re = scanCtp.p.match(line)
            if (re == None):
                continue
##data constraints
            tmp_list = scanCtp.record_2(re)
##insert records
            except sqlite3.Error as e:
                print 'insert record failed. %s' % e.args[0]
                scanErrFile.write(line)
        try:
            ifile.read()
            ifile.close()

if __name__ == '__main__':
    process();
