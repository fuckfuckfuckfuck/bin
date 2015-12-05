# 
from  pyalgotrade import bar

class myBasicBar(bar.BasicBar):
    def __init__(self, dateTime, open_, high, low, close, volume, openint, sgnvol = None, frequency = 60, adjClose = None):
        bar.BasicBar.__init__(self, dateTime, open_, high, low, close, volume, None, frequency)
        self.__openint = openint
        self.__sgnvol = sgnvol

    def getSgnvol(self):
        return self.__sgnvol

    def getOpenint(self):
        return self.__openint

    # def __setstate__(self, state):
    # (self.__dateTime,
    #     self.__open,
    #     self.__close,
    #     self.__high,
    #     self.__volume,
    #     self.__frequency,
    #     self.__useAdjustedValue) = state

    # def __getstate__(self):
    #         self.__open,
    #         self.__close,
    #         self.__high,
    #         self.__volume,
    #         self.__adjClose,
    #         self.__frequency,
    #         self.__useAdjustedValue
    #     )


