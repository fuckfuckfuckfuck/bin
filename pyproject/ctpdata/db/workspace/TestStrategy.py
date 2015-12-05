from pyalgotrade import strategy

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument

    def onBars(self, bars):
        bar = bars[self.__instrument]
        self.info("OHLCVOSngvol:%s %s %s %s %s %s %s" % (bar.getOpen(),bar.getHigh(),bar.getLow(),bar.getClose(),bar.getVolume(),bar.getOpenint(),bar.getSgnvol()))

