# -*- coding: utf-8 -*-

import datetime as dtime
from pyalgotrade.barfeed import sqlitefeed
from pyalgotrade.broker.backtesting import TradePercentage
from pyalgotrade import broker

from orb import ORB
from db import DB_SQLITE_PATH,DB_ORIGIN
import analyzer 

class myStrategy(ORB):
    def __init__(self,feed, symbol, myBroker,openrange,p_a,p_c,False):
        ORB(feed, symbol, myBroker,openrange,p_a,p_c,False)
        self.retAnalyzer = returns.Returns()
        myStrategy.attachAnalyzer(retAnalyzer)
        self.sharpeRatioAnalyzer = sharpe.SharpeRatio()
        myStrategy.attachAnalyzer(sharpeRatioAnalyzer)
        self.drawDownAnalyzer = drawdown.DrawDown()
        myStrategy.attachAnalyzer(drawDownAnalyzer)
        self.tradesAnalyzer = trades.Trades()
        myStrategy.attachAnalyzer(tradesAnalyzer)

    # def print(self):
        

symbol = "Y00"

feed = sqlitefeed.Feed(DB_SQLITE_PATH, 60, 20000)
startDtime = dtime.datetime(2015,5,21)
endDtime = dtime.datetime(2015,6,18)
feed.loadBars(symbol,None,startDtime,endDtime)

commission_y00 = 0.0001
commission = TradePercentage(commission_y00)
initEquity = 1000000
myBroker = broker.backtesting.Broker(initEquity, feed, commission)

openrange = 20
p_a = 1
p_c = 2
a = ORB(feed, symbol, myBroker,openrange,p_a,p_c,False, False) 

ANALYZE_ATTACH(a)
a.run()
ANALYZE_PRINT(a)
