
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

    def preInit(self):
        self.__data.candlesController.init(self.__ticker.getTicker(), self.__getCandlesAmountForInit())
        self.__data.atrController.init(self.__ticker.getPricePrecision())
        self.__data.averagesController.init(self.__ticker.getPricePrecision())
        self.__data.signalController.init(self.__ticker, self)

    def __getCandlesAmountForInit(self):
        amount = self.__data.averagesController.getCandlesAmountForInit()
        amount = max(amount, self.__data.atrController.getCandlesAmountForInit())
        return amount

    def isSync(self):
        return self.__data.candlesController.sync()

    def loop(self):
        for candle in self.__data.candlesController.getNotProcessedCandles():
            self.__data.averagesController.process(candle)
            self.__data.atrController.process(candle)
        self.__data.candlesController.markProcessed()

        #self.__data.atrController.process(self.__data.candlesController.getLastCandle()) # to do
        self.__data.signalController.update(self.__data.candlesController.getLastCandle())

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
