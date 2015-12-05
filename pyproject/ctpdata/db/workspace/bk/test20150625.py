
import datetime as dtime
from pyalgotrade.barfeed import sqlitefeed
from pyalgotrade import broker
from pyalgotrade.broker.backtesting import TradePercentage
from db import DB_SQLITE_PATH,DB_ORIGIN
from pyalgotrade import strategy

class test(strategy.BacktestingStrategy):
    def __init__(self,symbol):
        strategy.BacktestingStrategy.__init__(self,feed)
        self.__symbol = symbol
        self.counter = 0
        self.re = []

    def onBars(self, bars):
        self.counter = self.counter + 1
        bar = bars[self.__symbol]
        tmp = bar.getClose()
        self.re.append(tmp)

    def onFinish(self,bars):
        self.info(self.counter)
        self.info(len(self.re))

symbol = "IF00"
feed = sqlitefeed.Feed(DB_SQLITE_PATH,60,20000)
feed.loadBars(symbol,None,dtime.datetime(2015,5,21),dtime.datetime(2015,6,25))
a = test(symbol)
a.run()
print "aa"
a.stop()

