
from models import timeframe
from systems import atrController
from systems import rsiController
from systems import divergenceController
from systems import vertexController
from systems import candlesController

class TimeframeData:
    def __init__(self, tf: timeframe.Timeframe):
        self.timeframe = tf
        self.atrController: atrController.AtrController = atrController.AtrController()
        self.rsiController: rsiController.RsiController = rsiController.RsiController()
        self.vertexController: vertexController.VertexController = vertexController.VertexController()
        self.candlesController: candlesController.CandlesController = candlesController.CandlesController(tf)
        self.divergenceController: divergenceController.DivergenceController = divergenceController.DivergenceController()
        
class TimeframeController:
    def __init__(self, tf: timeframe.Timeframe, tckController):
        self.__ticker = tckController
        self.__data = TimeframeData(tf)
        self.__data.candlesController.init(self.__ticker.getTicker(), self.__getCandlesAmountForInit())
        self.__data.atrController.init(self.__data.candlesController, self.__ticker.getPricePrecision())
        self.__data.rsiController.init(self.__data.candlesController)
        self.__data.divergenceController.init(self.__data.candlesController)
        self.__data.vertexController.init(self.__data.candlesController)

    def __getCandlesAmountForInit(self):
        amount = self.__data.atrController.getCandlesAmountForInit()
        amount = max(amount, self.__data.rsiController.getCandlesAmountForInit())
        amount = max(amount, self.__data.divergenceController.getCandlesAmountForInit())
        return amount

    def isSync(self):
        return self.__data.candlesController.sync()

    def loop(self):
        self.__data.atrController.process()
        self.__data.rsiController.process()
        self.__data.vertexController.process()
        self.__data.divergenceController.process()

    def getTimeframe(self):
        return self.__data.timeframe
    def getAtrController(self):
        return self.__data.atrController
    def getCandlesController(self):
        return self.__data.candlesController
    def getDivergenceController(self):
        return self.__data.divergenceController
