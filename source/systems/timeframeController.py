
from models import candle
from systems import atrController
from systems import candlesController
from systems import movingAverageController
from systems import signalController

class TimeframeController:
    def __init__(self, ticker:str, tf: str):
        self.__averagesController = movingAverageController.MovingAverageController(tf)
        self.__atrController: atrController.AtrController = atrController.AtrController(ticker)
        self.__candlesController: candlesController.CandlesController = candlesController.CandlesController(ticker, tf, self.__getCandlesAmountForInit())
        self.__signalController: signalController.SignalController = signalController.SignalController(ticker, self.getAveragesController(), self.getCandlesController())
        self.__initControllers()
    
    def __getCandlesAmountForInit(self):
        amount = self.__averagesController.getCandlesAmountForInit()
        amount = max(amount, self.__atrController.getCandlesAmountForInit())
        return amount

    def __initControllers(self):
        for candle in self.__candlesController.getFinishedCandles():
            self.__averagesController.process(candle)
            self.__atrController.process(candle)

    def getAveragesController(self):
        return self.__averagesController
    
    def getAtrController(self):
        return self.__atrController
    
    def getCandlesController(self):
        return self.__candlesController

    def getSignalController(self):
        return self.__signalController

    def update(self):
        self.__signalController.update(self.__candlesController.getLastFinishedCandle()) #tmp get actual candle
