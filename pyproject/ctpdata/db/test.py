# from utility import interval_statistics_2
# import sqlite3
# import numpy as np

# con = sqlite3.connect("jzt_onemin_oop.db")
# cur = con.cursor()

# sqls = """select tradingday,updatetime,open,high,low,close,volume,amount,openint from oneminute where instrumentid = ? and tradingday > ? and tradingday <= ? order by tradingday ASC,updatetime ASC;"""

# cur.execute(sqls,("AX00",20150518,20150521))
# rows=cur.fetchall()

# ret_dtime = np.zeros((1,2), dtype = 'i4')
# ret_OHLC = np.zeros((1,4), dtype='f8')
# ret_VAO = np.zeros((1,3), dtype = 'i4')

# def interval_statistics_2(i,list_row,l,r):
#     # global ret_dtime,ret_OHLC,ret_VAO
#     print id(ret_dtime)
#     print id(list_row)
#     ret_dtime[i,0] = list_row[r][0]
#     # ret_dtime[i,1] = tmp_i_num
#     ret_OHLC[i,0] = list_row[l+1][2]
#     # ret_OHLC[i,1] = max(list_row[(l+1):(r+1)][3])
#     ret_OHLC[i,1] = max(list_row[i][3] for i in range(l+1,r+1))
#     # ret_OHLC[i,2] = min(list_row[(l+1):(r+1)][4])
#     ret_OHLC[i,2] = min(list_row[i][4] for i in range(l+1,r+1))
#     ret_OHLC[i,3] = list_row[r][5]
#     ret_VAO[i,0] = sum(list_row[i][6] for i in range(l+1,r+1))
#     ret_VAO[i,1] = sum(list_row[i][7] for i in range(l+1,r+1))
#     ret_VAO[i,2] = list_row[r][8]
    
# g=interval_statistics_2(0,rows,1,5) 
import datetime as dt

try:
    z=dt.datetime(-1,1,1)
except ValueError as e:
    print(e.args[0])



