# -*- coding: utf-8 -*-
## import copy
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades

import collections
resultOrb = collections.namedtuple('resultORB',['result','cumulativeReturns','sharpe','mdd','longestMdd','profits_mean','profits_std','profits_max','profits_min','returns_mean','returns_std','returns_max','returns_min'])

NULLVALUE = -200

# class analyzeResult(object):
#    def __init__(self):
        

def report_profit_return(get_count,get_profit,get_returns,ree):
    tmp = get_count()
    if 0 < tmp:
        profits = get_profit()
        # ree.append((profits.mean(),profits.std(),profits.max(),profits.min()))
        ree['profits_mean'] = profits.mean()
        ree['profits_std'] = profits.std()
        ree['profits_max'] = profits.max()
        ree['profits_min'] = profits.min()
        returns = get_returns()
        # ree.append((returns.mean() * 100, returns.std() * 100, returns.max() * 100, returns.min() * 100))
        ree['returns_mean'] = returns.mean() * 100
        ree['returns_std'] = returns.std() * 100
        ree['returns_max'] = returns.max() * 100
        ree['returns_min'] = returns.min() * 100
    else:
        ree['profits_mean'] = NULLVALUE
        ree['profits_std'] = NULLVALUE
        ree['profits_max'] = NULLVALUE
        ree['profits_min'] = NULLVALUE
        ree['returns_mean'] = NULLVALUE
        ree['returns_std'] = NULLVALUE
        ree['returns_max'] = NULLVALUE
        ree['returns_min'] = NULLVALUE


class ANALYZER(object):
    def __init__(self):
        self.retAnalyzer = returns.Returns()
        self.attachAnalyzer(self.retAnalyzer)
        self.sharpeRatioAnalyzer = sharpe.SharpeRatio()
        self.attachAnalyzer(self.sharpeRatioAnalyzer)
        self.drawDownAnalyzer = drawdown.DrawDown()
        self.attachAnalyzer(self.drawDownAnalyzer)
        self.tradesAnalyzer = trades.Trades()
        self.attachAnalyzer(self.tradesAnalyzer)
        # self.__re = resultOrb()
        self.__re = {}

    # def attach(self):
    #     self.retAnalyzer = returns.Returns()
    #     self.attachAnalyzer(retAnalyzer)
    #     sharpeRatioAnalyzer = sharpe.SharpeRatio()
    #     self.attachAnalyzer(sharpeRatioAnalyzer)
    #     drawDownAnalyzer = drawdown.DrawDown()
    #     self.attachAnalyzer(drawDownAnalyzer)
    #     tradesAnalyzer = trades.Trades()
    #     self.attachAnalyzer(tradesAnalyzer)

    def myPrint(self):
        print "Final portfolio value: $%.2f" % self.getResult()
        print "Cumulative returns: %.2f %%" % (self.retAnalyzer.getCumulativeReturns()[-1] * 100)
        print "Sharpe ratio: %.2f" % (self.sharpeRatioAnalyzer.getSharpeRatio(0.05))
        print "Max. drawdown: %.2f %%" % (self.drawDownAnalyzer.getMaxDrawDown() * 100)
        print "Longest drawdown duration: %s" % (self.drawDownAnalyzer.getLongestDrawDownDuration())

        print
        print "Total trades: %d" % (self.tradesAnalyzer.getCount())
        if self.tradesAnalyzer.getCount() > 0:
            profits = self.tradesAnalyzer.getAll()
            print "Avg. profit: $%2.f" % (profits.mean())
            print "Profits std. dev.: $%2.f" % (profits.std())
            print "Max. profit: $%2.f" % (profits.max())
            print "Min. profit: $%2.f" % (profits.min())
            returns = self.tradesAnalyzer.getAllReturns()
            print "Avg. return: %2.f %%" % (returns.mean() * 100)
            print "Returns std. dev.: %2.f %%" % (returns.std() * 100)
            print "Max. return: %2.f %%" % (returns.max() * 100)
            print "Min. return: %2.f %%" % (returns.min() * 100)

        print
        print "Profitable trades: %d" % (self.tradesAnalyzer.getProfitableCount())
        if self.tradesAnalyzer.getProfitableCount() > 0:
            profits = self.tradesAnalyzer.getProfits()
            print "Avg. profit: $%2.f" % (profits.mean())
            print "Profits std. dev.: $%2.f" % (profits.std())
            print "Max. profit: $%2.f" % (profits.max())
            print "Min. profit: $%2.f" % (profits.min())
            returns = self.tradesAnalyzer.getPositiveReturns()
            print "Avg. return: %2.f %%" % (returns.mean() * 100)
            print "Returns std. dev.: %2.f %%" % (returns.std() * 100)
            print "Max. return: %2.f %%" % (returns.max() * 100)
            print "Min. return: %2.f %%" % (returns.min() * 100)

        print
        print "Unprofitable trades: %d" % (self.tradesAnalyzer.getUnprofitableCount())
        if self.tradesAnalyzer.getUnprofitableCount() > 0:
            losses = self.tradesAnalyzer.getLosses()
            print "Avg. loss: $%2.f" % (losses.mean())
            print "Losses std. dev.: $%2.f" % (losses.std())
            print "Max. loss: $%2.f" % (losses.min())
            print "Min. loss: $%2.f" % (losses.max())
            returns = self.tradesAnalyzer.getNegativeReturns()
            print "Avg. return: %2.f %%" % (returns.mean() * 100)
            print "Returns std. dev.: %2.f %%" % (returns.std() * 100)
            print "Max. return: %2.f %%" % (returns.max() * 100)
            print "Min. return: %2.f %%" % (returns.min() * 100)


    def myAppend(self):    
        self.__re['result'] = self.getResult()
        self.__re['cumulativeReturns'] = self.retAnalyzer.getCumulativeReturns()[-1] * 100
        self.__re['sharpe'] = self.sharpeRatioAnalyzer.getSharpeRatio(0.05)
        self.__re['mdd'] = self.drawDownAnalyzer.getMaxDrawDown() * 100
        self.__re['longestMdd'] = self.drawDownAnalyzer.getLongestDrawDownDuration()

        report_profit_return(self.tradesAnalyzer.getCount, self.tradesAnalyzer.getAll, self.tradesAnalyzer.getAllReturns, self.__re)
        report_profit_return(self.tradesAnalyzer.getProfitableCount, self.tradesAnalyzer.getProfits, self.tradesAnalyzer.getPositiveReturns, self.__re)
        report_profit_return(self.tradesAnalyzer.getUnprofitableCount, self.tradesAnalyzer.getLosses, self.tradesAnalyzer.getNegativeReturns, self.__re)
        # print len(re)
        # print "%f,%f,%f " % (re[0],re[2],re[3])
        # print id(re)
#        tmp = copy.deepcopy(re)
#        print tmp[2]

        # return self.__re
        return resultOrb(self.__re['result'],self.__re['cumulativeReturns'],self.__re['sharpe'],self.__re['mdd'],self.__re['longestMdd'],self.__re['profits_mean'],self.__re['profits_std'],self.__re['profits_max'],self.__re['profits_min'],self.__re['returns_mean'],self.__re['returns_std'],self.__re['returns_max'],self.__re['returns_min'])



        
