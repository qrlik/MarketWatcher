
from models import timeframe
from systems import atrController
from systems import candlesController
from systems import movingAverageController
from systems import signalController

class TimeframeData:
    def __init__(self, tf: timeframe.Timeframe):
        self.timeframe = tf
        self.averagesController: movingAverageController.MovingAverageController = movingAverageController.MovingAverageController(tf)
        self.atrController: atrController.AtrController = atrController.AtrController()
        self.candlesController: candlesController.CandlesController = candlesController.CandlesController(tf)
        self.signalController: signalController.SignalController = signalController.SignalController()
        
class TimeframeController:
    def __init__(self, tf: timeframe.Timeframe, tckController):
        self.__ticker = tckController
        self.__data = TimeframeData(tf)

    def init(self):
        self.__data.atrController.setPrecision(self.__ticker.getPricePrecision())
        self.__data.candlesController.init(self.__ticker, self.__getCandlesAmountForInit())
        self.__data.signalController.init(self.__ticker.getTicker(), self)
        for candle in self.__data.candlesController.getFinishedCandles():
            self.__data.averagesController.process(candle)
            self.__data.atrController.process(candle)

    def __getCandlesAmountForInit(self):
        amount = self.__data.averagesController.getCandlesAmountForInit()
        amount = max(amount, self.__data.atrController.getCandlesAmountForInit())
        return amount

    def update(self):
        self.__data.signalController.update(self.__data.candlesController.getLastFinishedCandle()) #tmp get actual candle

    def getTimeframe(self):
        return self.__data.timeframe
    def getAveragesController(self):
        return self.__data.averagesController
    def getAtrController(self):
        return self.__data.atrController
    def getCandlesController(self):
        return self.__data.candlesController
    def getSignalController(self):
        return self.__data.signalController
