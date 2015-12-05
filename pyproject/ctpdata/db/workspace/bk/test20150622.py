
import datetime as dtime
from pyalgotrade.barfeed import sqlitefeed
from pyalgotrade import broker
from pyalgotrade.broker.backtesting import TradePercentage
from db import DB_SQLITE_PATH,DB_ORIGIN

import orb
import analyzer

class subClass(orb.ORB, analyzer.ANALYZER):
    def __init__(self,feed,instrument,broker,openrange,p_a,p_c,isFinancialFuture):
        # super(subClass, self).__init__(feed,instrument,broker,openrange,p_a,p_c,isFinancialFuture)
        # super(subClass, self).__init__()
        orb.ORB.__init__(self,feed,instrument,broker,openrange,p_a,p_c,isFinancialFuture)
        analyzer.ANALYZER.__init__(self)

def process(symbol, orr, isFinancialFuture):
    feed = sqlitefeed.Feed(DB_SQLITE_PATH, 60, 14000)
    feed.loadBars(symbol,None,dtime.datetime(2015,5,21),dtime.datetime(2015,6,25))
    commission_y00 = 0.0001 
    commission = TradePercentage(commission_y00)
    brokerr =  broker.backtesting.Broker(20000000, feed, commission) 

    # orr = 15 
    a = subClass(feed, symbol, brokerr, orr, 1, 2, isFinancialFuture)
    a.run()
    return a.myAppend()


# list_symbols = ["AG00","AX00","CF00","CU00","FG00","I00","J00","JD00","JM00","L00","M00","MA00","NI00","P00","PP00","RB00","RM00","RU00","SRX00","TA00","TC00","AU00","C00","OI00","Y00"]
# list_symbols = ["JM00","NI00"]
list_symbols = ["IF00","IC00","IH00"]
re = []
for ss in list_symbols:
    for i in range(10,60,2):
    # for i in range(42,49,1):
        tmp = process(ss, i, True)
        re.append(tmp)

# symbol ="Y00"
# feed = sqlitefeed.Feed(DB_SQLITE_PATH, 60, 2000)
# feed.loadBars(symbol,None,dtime.datetime(2015,5,21),dtime.datetime(2015,6,25))
# commission_y00 = 0.0001
# commission = TradePercentage(commission_y00)
# brokerr =  broker.backtesting.Broker(1000000, feed, commission)

# orr = 15
# a = subClass(feed, symbol, brokerr, orr, 1, 2, False)
# a.run()
# b = a.myAppend()

for i in xrange(len(re)):
    tmp = int(i / 25)
    if 0 == i - tmp*25:
        print list_symbols[tmp]
    print re[i].sharpe

