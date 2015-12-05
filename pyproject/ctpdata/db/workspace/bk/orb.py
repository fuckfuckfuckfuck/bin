# -*- coding: utf-8 -*-
# Mark Fisher

import datetime as dtime

from pyalgotrade import strategy
# from pyalgotrade.barfeed import sqlitefeed
from pyalgotrade import broker
from pyalgotrade import bar



class ORB(strategy.BacktestingStrategy):
    def __resetORHL(self):
        self.orh = 0
        self.orl = 1000000
        self.barIntradayCount = 0

    def __resetCounter(self):
        self.counter_aPlus = 0
        self.counter_aMinus = 0
        self.counter_cPlus = 0
        self.counter_cMinus = 0

    def __init__(self,feed,instrument,broker,openrange,p_a,p_c,isFinancialFuture):
        strategy.BacktestingStrategy.__init__(self,feed,broker)
        self.__position = None
        self.__instrument = instrument
        # self.__prices = feed[instrument].getCloseDataSeries()
        self.stateA = 0 # 1 dup -1 kong 0 inited
        self.stateB = 6 # 2 openduo 3 closeduo 4 openkong 5 closekong 6 empty
        self.openrange = openrange
        self.barsLimit = int(self.openrange / 2) + 1
        self.a_plus = 0
        self.a_minus = 0
        self.c_plus = 0
        self.c_minus = 0
        self.p_a = p_a
        self.p_c = p_c

        self.lastDate = None
        self.__resetORHL()
        self.__resetCounter()
        if (isFinancialFuture):
            self.exitIntradayTradeTime = dtime.time(15,15)
        else:
            self.exitIntradayTradeTime = dtime.time(18,50)

        self.__clos = -1
        self.__timeLimitInSeconds = self.openrange*60 ## in seconds 


    def __resetAC(self): 
        tmp_ob = self.orh - self.orl 
        if (0 >= tmp_ob):
            print "zero or negative OR, return!"
            return
        self.a_plus = self.orh + self.p_a*tmp_ob
        self.a_minus = self.orl - self.p_a*tmp_ob
        self.c_plus = self.orh + self.p_c*tmp_ob
        self.c_minus = self.orl - self.p_c*tmp_ob


    def __dynamics(self,close):
        if (0 < self.counter_aPlus):
            if (self.a_plus >= close):
                self.counter_aPlus = 0
                if (self.c_minus > close):
                    self.counter_cMinus = 1
                elif (self.a_minus > close):
                    self.counter_aMinus = 1
            else:
                self.counter_aPlus += 1
        elif (0 < self.counter_aMinus):
            if (self.a_minus <= close):
                self.counter_aMinus = 0
                if (self.c_plus < close):
                    self.counter_cPlus = 1
                elif (self.a_plus < close):
                    self.counter_aPlus = 1
        elif (0 == self.counter_cPlus and 0 == self.counter_cMinus):
            if (self.c_plus < close):
                self.counter_cPlus = 1
            elif (self.a_plus < close):
                self.counter_aPlus = 1
            elif (self.c_minus > close):
                self.counter_cMinus = 1
            elif (self.a_minus > close):
                self.counter_aMInus = 1
        elif (0 < self.counter_cPlus):
            if (self.c_plus >= close):
                self.counter_cPLus = 0
                if (self.c_minus > close):
                    self.counter_cMinus = 1
                elif (self.a_minus > close):
                    self.counter_aMinus = 1
            else:
                self.counter_cPlus += 1
        else:
            if (self.c_minus <= close):
                self.counter_cMinus = 0
                if (self.c_plus < close):
                    self.counter_cPlus = 1
                elif (self.a_plus < close):
                    self.counter_aPlus = 1
            else:
                self.counter_cMinus += 1


    def processEvent1(self):
        if (self.barsLimit < self.counter_cPlus):
            return 2 # c_plus
        elif (self.barsLimit < self.counter_cMinus):
            return -2 # c_minus
        elif (self.barsLimit < self.counter_aPlus + self.counter_cPlus):
            return 1 # a_plus
        elif (self.barsLimit < self.counter_aMinus + self.counter_cMinus):
            return -1 # a_minus
        return 0

    def processEvent2(self, close):
    ## MAYBE OBSOLETE
        if (close < self.orl):
            return -1 # stoplossprice_duo
        elif (close > self.orh):
            return 1 # stoplossprice_kong
        return 0

    def processEvent3(self):
        if (self.__position.isOpen() and self.__position.getAge().seconds > self.__timeLimitInSeconds):
            tmp_2 = self.__position.getPnL()
            if (tmp_2 < 0):
                return 1 # stoploss_time
        return 0

    def allocateShares(self):
        if 0 < self.__clos:
            return int(self.getBroker().getCash()*0.5/self.__clos)
        else:
            self.info("Wrong clos!!! %.2f" % self.__clos)

    def action_init2up(self):
        self.stateA = 1
        self.stateB = 2
        shares = self.allocateShares()
        self.__position = self.enterLong(self.__instrument,shares, True)

    def action_init2down(self):
        self.stateA = -1
        self.stateB = 4
        shares = self.allocateShares()
        self.__position = self.enterShort(self.__instrument,shares,True)

    def action_upempty2duo(self):
        self.stateB = 2
        shares = self.allocateShares()
        self.__position = self.enterLong(self.__instrument,shares, True)

    def action_downempty2duo(self):
        self.stateB = 2
        shares = self.allocateShares()
        self.__position = self.enterLong(self.__instrument,shares, True)

    def action_upempty2kong(self):
        self.stateB = 4
        shares = self.allocateShares()
        self.__position = self.enterShort(self.__instrument,shares,True)

    def action_downempty2kong(self):
        self.stateB = 4
        shares = self.allocateShares()
        self.__position = self.enterShort(self.__instrument,shares,True)

    # ((1,4), 5, price stop)
    # def action_upkong2exit_price(self):

    def action_upkong2exit_time(self):
        self.stateB = 5
        if (self.__position.exitActive()):
            self.__position.cancelExit()                        
        self.__position.exitMarket()
        self.__resetCounter()

    # ((-1,2),3, price stop)
    # def action_downduo2exit_price(self):

    def action_downduo2exit_time(self):
        self.stateB = 3
        if (self.__position.exitActive()):
            self.__position.cancelExit()            
        self.__position.exitMarket()
        self.__resetCounter()

    # ((1,2), 3, price stop)
    # def action_upduo2exit_price(self):

    def action_upduo2exit_time(self):
        self.stateB = 3
        if (self.__position.exitActive()):
            self.__position.cancelExit()            
        self.__position.exitMarket()
        self.__resetCounter()

    # ((-1,4),5, price stop)
    # def action_downkong2exit_price(self):

    def action_downkong2exit_time(self):
        self.stateB = 5
        if (self.__position.exitActive()):
            self.__position.cancelExit()            
        self.__position.exitMarket()
        self.__resetCounter()        

    def exitAllPositions(self):
        if (None != self.__position):
            if (self.__position.exitActive()):
                self.__position.cancelExit()
                self.debug("cancelExit")
            self.__position.exitMarket()
            self.__resetCounter()

    def onBars(self, bars):
        bar = bars[self.__instrument]
        # tmp_dtime = bar.getDateTime()
        self.__dtime = bar.getDateTime()
        if (None is self.lastDate):
            self.lastDate = self.__dtime.date()
        else:
            if (self.lastDate != self.__dtime.date()):
                self.lastDate = self.__dtime.date()
                self.__resetORHL()                
            else:
                self.barIntradayCount += 1

        ## intraday dynamics
        if (self.openrange > self.barIntradayCount):
            if bar.getHigh() > self.orh:
                self.orh = bar.getHigh()
            if bar.getLow() < self.orl:
                self.orl = bar.getLow()
        elif (self.openrange == self.barIntradayCount):
            self.__resetAC()
        elif (self.__dtime.time() > self.exitIntradayTradeTime):
            self.exitAllPositions()
        else:
            self.__clos = bar.getClose()
            self.__dynamics(self.__clos)
            if (0 == self.stateA):
                tmp_0 = self.processEvent1()
                if (1 <= tmp_0):
                    self.action_init2up()
                elif (-1 >= tmp_0):
                    self.action_init2down()
            else:
                if (1 == self.stateA):
                    if (6 == self.stateB):
                        tmp_6 = self.processEvent1()
                        if (1 <= tmp_6):
                            self.action_upempty2duo()
                        elif (-2 == tmp_6):
                            self.action_upempty2kong()
                    elif (2 == self.stateB):
                        tmp_2 = self.processEvent3()
                        if (1 == tmp_2):
                            self.action_upduo2exit_time()
                    elif (4 == self.stateB):
                        tmp_4 = self.processEvent3()
                        if (1 == tmp_4):
                            self.action_upkong2exit_time()
                else: # self.stateA == -1
                    if (6 == self.stateB):
                        tmp_6 = self.processEvent1()
                        if (2 == tmp_6):
                            self.action_downempty2duo()
                        elif (-1 >= tmp_6):
                            self.action_downempty2kong()
                    elif (2 == self.stateB):
                        tmp_2 = self.processEvent3()
                        if (1 == tmp_2):
                            self.action_downduo2exit_time()
                    elif (4 == self.stateB):
                        tmp_4 = self.processEvent3()
                        if (1 == tmp_4):
                            self.action_downkong2exit_time()


    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        ## check
        shares = position.getShares()
        if ((shares > 0 and 2 != self.stateB) or 
            (shares < 0 and 4 != self.stateB) or 
            0 == shares):
            self.info("Inconsistent signs:(shares %i, stateB %i" % (shares,self.stateB))
        
        if 0 < shares:
            self.info("Buy at %.2f" % (execInfo.getPrice()))
            self.__position.exitStop(self.orl, True)
        elif 0 > shares:
            self.info("Sellshort at %.2f" % (execInfo.getPrice()))
            self.__position.exitStop(self.orh, True)
    
    def onExitOk(self, position):
        order = position.getExitOrder()
        if (None == order):
            self.info("wrong: empty order!return.")
            return
        elif (broker.Order.Type.STOP == order.getType()):
            order_type = "stop"
        else:
            order_type = "market"
        
        tmp_info = order.getExecutionInfo()
        order_price = tmp_info.getPrice()
        
        condition1 = (3 == self.stateB) or (self.__dtime.time() > self.exitIntradayTradeTime)
        condition2 = (5 == self.stateB) or (self.__dtime.time() > self.exitIntradayTradeTime)
        
        if (broker.Order.Action.SELL == order.getAction() and 
            condition1):
            self.info("Finish: sell and exitLong:price %.2f, type %s." % (order_price, order_type))
        elif (broker.Order.Action.BUY_TO_COVER == order.getAction() and 
            condition2):
            self.info("Finish: buytocover and exitShort:price %.2f, type %s." % (order_price, order_type))       
        else: 
            qty = order.getExecutionInfo().getQuantity()
            self.info("Fail to exit: price:%.2f quantity:%i, stateB:%i." % (order_price, qty, self.stateB))
            return

        self.stateB = 6
        if (self.__position.exitFilled()):
            self.__position = None
        else:
            self.info("After exit, position is not empty:shares:%i" % self.__position.getShares())
