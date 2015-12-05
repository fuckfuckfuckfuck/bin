#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import logging
import string
import numpy as np
import datetime as dtime

from pyalgotrade import strategy
from pyalgotrade.barfeed import sqlitefeed
from pyalgotrade.technical import ma
from pyalgotrade import broker

# DB_SQLITE_PATH = "pyalgo_1min.db"
# DB_ORIGIN = "jzt_onemin_oop.db"
from db import DB_SQLITE_PATH
from db import DB_ORIGIN


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        strategy.BacktestingStrategy.__init__(self, feed, 1000000)
        self.__position = None
        self.__instrument = instrument
        # We'll NOT use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(False)
        # self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), smaPeriod)
        self.__sma = ma.SMA(feed[instrument].getCloseDataSeries(), smaPeriod)

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
        # Check if we have to exit the position.
        elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():
            self.__position.exitMarket()


def run_strategy(smaPeriod):
    # Load the yahoo feed from the CSV file
    feed = sqlitefeed.Feed(DB_SQLITE_PATH, 60, 2000)
    feed.loadBars("Y00",None,dtime.datetime(2015,5,21),dtime.datetime(2015,5,25))

    # Evaluate the strategy with the feed.
    myStrategy = MyStrategy(feed, "Y00", smaPeriod)
    myStrategy.run()
    print "Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity()
    myStrategy.run()

run_strategy(40)

