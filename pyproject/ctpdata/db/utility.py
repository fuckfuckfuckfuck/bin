import string
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

def timeFill(strs):
    tmp = string.atoi(strs)
    if (tmp<0 or tmp >60):
        print(strs + " is Out of Range!Exit.")
        return
    if (tmp < 10):
        return("0" + str(tmp))
    return(strs)

# DB_SQLITE_PATH = "D:\\bin\\pyproject\\ctpdata\\jzt_onemin.db"
sql_jzt_onemin ="""
CREATE TABLE if not exists `oneminute` (
  `tradingday` INT NOT NULL,
  `updatetime` INT NOT NULL,
  `instrumentid` TEXT NOT NULL,
  `open` double NOT NULL,
  `high` double NOT NULL,
  `low` double NOT NULL,
  `close` double NOT NULL,
  `volume` int NOT NULL,
  `amount` int NOT NULL,
  `openint` int NOT NULL,
  PRIMARY KEY (`instrumentid`,`tradingday`,`updatetime`)
)
"""

################################################################        
sql_jzt_tExchange = """ 
CREATE TABLE IF NOT EXISTS `exchanges` (
	id TEXT NOT NULL,
	name TEXT NOT NULL,
	date_start INT NOT NULL,
	date_last INT NOT NULL,
	manual_flag INT NOT NULL,
	update_time TEXT NOT NULL,
	PRIMARY KEY (id)
);
"""

######################################################

sql_jzt_tSectors = """
CREATE TABLE if not exists `sectors` (
	id INT,
	sector TEXT NOT NULL,
	name TEXT ,
	min_date INT,
	max_date INT,
	exchange TEXT NOT NULL,
	manual_flag INT NOT NULL,	
	update_time TEXT NOT NULL,
	PRIMARY KEY (sector,exchange)
)		
"""

sql_jzt_tSectors_insert = """insert into sectors(sector,exchange,manual_flag,update_time) values (?,?,0,datetime()); """
#####################################################

sql_jzt_tContracts = """
CREATE TABLE if not exists `contracts` (
	instrumentid TEXT NOT NULL,
	min_date INT,
	max_date INT,
	sector TEXT NOT NULL,
	manual_flag INT NOT NULL,	
	update_time INT NOT NULL,
	PRIMARY KEY (instrumentid,sector)
)		
"""

sql_jzt_tContracts_insert = """insert into contracts(instrumentid,sector,manual_flag,update_time) values (?,?,0,datetime()); """

#####################################################

sql_jzt_tTradingday = """
CREATE TABLE IF NOT EXISTS `tradingday` (
	tradingday INT UNIQUE NOT NULL
)
"""

sql_jzt_tTradingday_insert = """insert into tradingday (tradingday) values (?);"""

#########################
sql_jzt_drawing = """
CREATE TABLE IF NOT EXISTS `continuous` (
  instrumentid TEXT UNIQUE NOT NULL
)
"""

sql_jzt_drawing_insert = """
insert into continuous 
select instrumentid from oneminute 
where
updatetime >= 130000 and updatetime <= 190000 and '00' = substr(instrumentid,length(instrumentid)-1,2) 
group by instrumentid  having count(*) >= 226 
"""

########################################################
sql_jzt_main = """
select close,volume,amount,openint from oneminute where 
tradingday = ? and 
instrumentid = ? and updatetime > 130000 and updatetime < 190000 and substr(updatetime,1,length(updatetime)-2) != "1530" and
substr(instrumentid,1,2) not in ("SH","SZ")
order by updatetime ASC;
"""

# sql_jzt_continu = """
# select close,volume,amount,openint from oneminute where 
# tradingday = ? and 
# instrumentid = ? and updatetime > 130000 and updatetime < 190000 and substr(updatetime,1,length(updatetime)-2) != "1530" and
# substr(instrumentid,1,2) not in ("SH","SZ")
# order by updatetime ASC;
# """

sql_jzt_continu_select = """
select instrumentid from oneminute 
where 
tradingday = ? and updatetime > ? and substr(updatetime,1,length(updatetime)-2) != ? and
updatetime <= ? and "00" = substr(instrumentid,length(instrumentid)-1,2) 
group by instrumentid having count(*) >= ? order by instrumentid 
"""
#"""
#select instrumentid from oneminute 
#where 
#tradingday = ? and updatetime > 132000 and substr(updatetime,1,length(updatetime)-2) != 1530 and
#updatetime <= 185000 and "00" = substr(instrumentid,length(instrumentid)-1,2) 
#group by instrumentid having count(*) >= ? 
#"""

sql_jzt_continu_select_2 = """
select instrumentid from oneminute 
where 
tradingday = ? and updatetime > ? and updatetime <= ? and "00" = substr(instrumentid,length(instrumentid)-1,2) 
group by instrumentid having count(*) >= ? order by instrumentid 
"""

sql_jzt_main_select = """
select instrumentid from main where substr(instrumentid,1,2) not in ("SH","SZ");
"""

sql_jzt_continu_select_len = """
select distinct substr(updatetime,1,4) from oneminute where instrumentid in 
    (select * from continuous) and tradingday=?;
"""


# trinity(list_continu_data)


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

def trinity(nparray):
    # (226,4) close,vol,amount,openint
    tmp_n = np.abs(nparray[-1,0] - nparray[0,0])
    efficiency = np.sum(np.abs(np.diff(nparray[:,0])))
    if (0.0001 <= efficiency):
        efficiency = tmp_n / efficiency 
    else:
        efficiency = 0

    tmp_n1 = sum(nparray[:,1])
    if (0 != nparray[-1,3]):
        hot = tmp_n1 / nparray[-1,3]
    else:
        hot = 0

    tmp_n = np.diff(np.log(nparray[:,0]))
    realized_volatility = np.sqrt(np.sum(tmp_n*tmp_n))  
    return((efficiency, hot, realized_volatility))

def my_corr_matrix(nparray):
#    column vector to row vector
#diff log prices
    tmp = np.log(np.transpose(nparray))
    tmp_1 = np.corrcoef(np.diff(tmp))
    return(tmp_1)


##############mktvital####################
sql_jzt_mktvital_insert = """
insert into mktvital
select ?,?,?,?,?,0,datetime() ;
"""

def my_str(uni_codes):
    re = uni_codes[0][0]
    for i in range(1,len(uni_codes[0])):
        re = re + uni_codes[0][i]
    return(str(re))


###############tradingtime############
sql_jzt_tradingtime = """
CREATE TABLE IF NOT EXISTS `tradingtime` (
tradingtime INT NOT NULL,
isjzttime INT NOT NULL,
PRIMARY KEY (tradingtime, isjzttime)
)
"""

sql_jzt_tradingtime_insert = """
INSERT OR IGNORE INTO tradingtime 
select distinct cast(substr(updatetime,1,length(updatetime)-2) as integer) as dt, 1 from oneminute 
where instrumentid NOT in (
select distinct instrumentid from contracts where sector in (select distinct sector from sectors where exchange = "ZJ")
) 
and
dt >= 100 and dt <= 1900 order by dt ASC;
"""

################jzt_resample#################
def scan_regex_append_errorfile(abs_fstr,pattern,ret,errorFile):
    fstr = open(abs_fstr, 'r')
    lines = fstr.readlines()
    for row in lines:
        row = row.strip()
        ret2 = pattern.match(row)
        if (None == ret2):
            # errorFile.write(line+'\n')        
            errorFile.write(row + '\n')
            continue
        ret2 = ret2.groups()
        ret.append(ret2)

    try:
        fstr.read()
    finally:
        fstr.close()


def fetch_append(sqls, cursor, logger, list_ret, err_msg, argss):    
    try:
        cursor.execute(sqls, argss)
    except sqlite3.Error as err:
        logger.error(err_msg +'|'+ err.args[0])
        return
    tmp_f_a = cursor.fetchall()
    if (None == tmp_f_a):
        logger.error(err_msg)
        return
    for i in tmp_f_a:
        list_ret.append(my_str(i))


def generate_x_y(prob_map):
    s = prob_map.shape
    x, y = np.meshgrid(np.arange(s[0]), np.arange(s[1]))
    return x.ravel(), y.ravel()

def heatmap(prob_map):
    x, y = generate_x_y(prob_map)
    plt.figure()
    plt.hexbin(x, y, C=prob_map.ravel())

def drawing_test():
    probs = np.random.rand(200, 200)
    heatmap(probs)
    plt.show()

def interval_statistics(left,right,re2,re3,re4,logger,BAccuVol=True):    
    # (tmp_i_last,i]   

    if (left > right):
        logger.error("Left:%(left)s is bigger than right:%(right)s. Exit." % {'left':left, 'right':right})
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
        if (BAccuVol):
            volume = re4[right][0] - re4[left][0]
            amount = re4[right][1] - re4[left][1]
        else:
            # volume = re4[right][0]
            volume = sum(re4[i][0] for i in range(left+1,right+1))
            amount = sum(re4[i][1] for i in range(left+1,right+1))
        openint = re4[right][2]
        for i in range(left+1,right+1):
            # the case when left++ > right is avoided by demanding left<right
            high = max(high, re3[i][0])
            low = min(low, re3[i][0])
            # volume = volume + re4[i][0]

    return (open,high,low,close,volume,amount,openint)


# ret_data,ret_idx should be empty list.
def resample_jzt(list_re2,list_re3,list_re4,logger,k,ret_data,ret_idx ):
    tmp_interval_length = 100*k
    tmp_i_last = 0
    tmp_i_num = int(list_re2[0,0][1] / tmp_interval_length)
    tmp_length = len(list_re2)

    for i in range(1, tmp_length):
        if ((tmp_length - 1) != i):
            tmp = int(list_re2[i][0][1] / tmp_interval_length)
            if (tmp_i_num != tmp): # old interval forms!
                # (tmp_i_last,i] : left open, right closed     
                tmp_data_1 = interval_statistics(tmp_i_last, i,list_re2,list_re3,list_re4, logger) # OHLCVAO
                if (None != tmp_data_1):
                    ret_data.append((list_re2[i][0][1], tmp_data_1))
                    ret_idx.append(i)
                    tmp_i_last = i
                    tmp_i_num = tmp
        else:
            tmp_data_1 = interval_statistics(tmp_i_last, i,list_re2,list_re3,list_re4,logger)
            if (None != tmp_data_1):
                ret_data.append((list_re2[i][0][1], tmp_data_1))
                ret_idx.append(i)

# interval_statistics_2(i,rows,tmp_idx[i-1],tmp_idx[i]):
def interval_statistics_2(i,list_row,l,r,ret_dtime,ret_OHLC,ret_VAO):
    # global ret_dtime,ret_OHLC,ret_VAO
    ret_dtime[i,0] = list_row[r][0]
    ret_dtime[i,1] = int(list_row[r][1] / 100) # only minutes!
    ret_OHLC[i,0] = list_row[l+1][2]
    ret_OHLC[i,1] = max(list_row[i][3] for i in range(l+1,r+1))
    ret_OHLC[i,2] = min(list_row[i][4] for i in range(l+1,r+1))
    ret_OHLC[i,3] = list_row[r][5]
    ret_VAO[i,0] = sum(list_row[i][6] for i in range(l+1,r+1))
    ret_VAO[i,1] = sum(list_row[i][7] for i in range(l+1,r+1))
    ret_VAO[i,2] = list_row[r][8]
    # print id(ret_dtime)
    # print ret_dtime[i,:]
    # print ret_OHLC[i,:]
    # print ret_VAO[i,:]
    

def selectdate_resample(symbol,date1,date2,resample_frequency,conn,cursor):
    # (,] interval
    symbol = str(symbol)
    symbol = symbol.strip()
    sqls = """select tradingday,updatetime,open,high,low,close,volume,amount,openint from oneminute where instrumentid = ? and tradingday > ? and tradingday <= ? order by tradingday ASC,updatetime ASC;"""
    if (date1 > date2):
        print("date1 bigger than date2!return")
        return
    elif (date1 == date2):
        date1 = date1 -1

    try:
        cursor.execute(sqls,(symbol,date1,date2))
    except sqlite3.Error as err:
        print("selectdate_resample failed to select:%s" % err.args[0])
    rows = cursor.fetchall()
    if (None == rows):
        print("selectdate_resample failed to fetchall. return.")
        return
    
    ## resampling
    tmp_idx = []
    tmp_interval_length = 100*resample_frequency
    tmp_i_last = 0
    tmp_length = len(rows)
    tmp_i_num = int (rows[0][1] / tmp_interval_length)
    tmp_s_r_len = len(rows)
    for i in xrange(tmp_s_r_len):
        tmp_s_r = int (rows[i][1] / tmp_interval_length)
        if (tmp_s_r != tmp_i_num): 
            # old interval forms!
            tmp_idx.append(i) 
            tmp_i_last = i
            tmp_i_num = tmp_s_r

    if (0 == len(tmp_idx)):
        ret_dtime = np.zeros((1,2), dtype = 'i4')
        ret_OHLC = np.zeros((1,4), dtype='f8')
        ret_VAO = np.zeros((1,3), dtype = 'i4')
        # ret_dtime[0,0] = rows[-1][0]
        # ret_dtime[0,1] = tmp_i_num
        # ret_OHLC[0,0] = rows[0][2]
        # ret_OHLC[0,1] = max(rows[:][3])
        # ret_OHLC[0,2] = min(rows[:][4])
        # ret_OHLC[0,3] = rows[-1][5]
        # ret_VAO[0,0] = sum(rows[:][6])
        # ret_VAO[0,1] = sum(rows[:][7])
        # ret_VAO[0,2] = rows[-1][8]
        # print "before,ret_dtime's id:%s\n" % id(ret_dtime)
        interval_statistics_2(0,rows,-1,tmp_length,ret_dtime,ret_OHLC,ret_VAO)

        return ret_dtime,ret_OHLC,ret_VAO
    elif ((tmp_s_r_len - 1) != tmp_idx[-1]):
        # the last endpoints!
        tmp_idx.append(tmp_s_r_len - 1)

    tmp_s_r_ret_len = len(tmp_idx) # bigger than 0
    ret_dtime = np.zeros((tmp_s_r_ret_len,2), dtype = 'i4')
    ret_OHLC = np.zeros((tmp_s_r_ret_len,4), dtype='f8')
    ret_VAO = np.zeros((tmp_s_r_ret_len,3), dtype = 'i4')
    tmp_idx.insert(0,-1)    
        
    for i in range(1, tmp_s_r_ret_len + 1):
        # print "before,ret_dtime's id:%s\n" % id(ret_dtime)
        interval_statistics_2(i - 1,rows,tmp_idx[i-1],tmp_idx[i],ret_dtime,ret_OHLC,ret_VAO) ## //** (,]
    return ret_dtime,ret_OHLC,ret_VAO


sql_jzt_continu_determine_len = """
select count(*) from (
select distinct substr(updatetime,1,length(updatetime)-2) as dt 
from oneminute where 
updatetime > ? and dt != ? and 
updatetime <= ? and
instrumentid not in (select instrumentid from contracts where sector in (select sector from sectors where exchange == 'ZJ'))
); 
"""
#select count(*) from (
#select distinct substr(updatetime,1,length(updatetime)-2) as dt 
#from oneminute where 
#updatetime > 132000 and dt != 1530 and 
#updatetime <= 185000 and
#instrumentid not in (select instrumentid from contracts where sector in (select sector from sectors where exchange == 'ZJ'))
#); 
#"""    
        
