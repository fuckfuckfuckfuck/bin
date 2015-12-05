## to scan data inexcel from SHFE .##

# import numpy as np
import sqlite3
import logging
import string
import re
db_file="exchange.db"
abs_dir="/home/dell/data/SHFE201508.csv"
error_dir="error.txt"
FORMAT='(asctime)-15s - %(levelname)-6s - %(message)s'
expression="(\w+)?,(\d+),(\d+\.?\d*)?,(\d+\.?\d*)?,(\d+\.?\d*)?,(\d+\.?\d*)?,(\d+\.?\d*)?,(\d+\.?\d*),(\d+\.?\d*),(-?\d+\.?\d*),(-?\d+\.?\d*),(\d+),(\d+\.?\d*),(\d+)\n"
p=re.compile(expression)
fstr_err=open(error_dir,'a')
logging.basicConfig(filename="scan201508_.log",format=FORMAT,level=logging.DEBUG)
logger=logging.getLogger('scan')
fstr=open(abs_dir,'r')


## create table
try:
    con=sqlite3.connect(db_file)
except sqlite3.Error as err:
    logger.warning("connection failed, ret=%s", err.args[0])
    raw_input("Failed connection. Press a key")

## scan and insert daily data

lines=fstr.readlines()
for line in lines:
    tmp=p.match(line.strip())
    if (tmp is None):
        fstr_err.write(line+'\n')
        continue
    tmp1=tmp.groups()

# consistency checking (? matching)
    if ('0'==tmp1[11]):
        tmp2 = (tmp1[0] is None) and (tmp1[4] is None) and (tmp1[5] is None) and (tmp1[6] is None)
        if (not tmp2):
            fstr_err.write(line+'\n')
            continue
    else:
        tmp3 = (tmp1[0] is not None) and (tmp1[4] is not None) and (tmp1[5] is not None) and (tmp1[6] is not None)
        if (not tmp3):
            fstr_err.write(line+'n')
            continue
   
# insertion

try:
    fstr.read()
finally:
    fstr.close()

fstr_err.close()



