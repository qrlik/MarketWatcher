
from models import timeframe
from systems import atrController
from systems import rsiController
from systems import divergenceController
from systems import vertexController
from systems import candlesController
from systems import signalController

class TimeframeData:
    def __init__(self, tf: timeframe.Timeframe):
        self.timeframe = tf
        self.atrController: atrController.AtrController = atrController.AtrController()
        self.rsiController: rsiController.RsiController = rsiController.RsiController()
        self.vertexController: vertexController.VertexController = vertexController.VertexController()
        self.candlesController: candlesController.CandlesController = candlesController.CandlesController(tf)
        self.divergenceController: divergenceController.DivergenceController = divergenceController.DivergenceController()
        self.signalController: signalController.SignalController = signalController.SignalController()
        
class TimeframeController:
    def __init__(self, tf: timeframe.Timeframe, tckController):
        self.__ticker = tckController
        self.__data = TimeframeData(tf)
        self.__data.candlesController.init(self.__ticker.getTicker(), self.__getCandlesAmountForInit())
        self.__data.atrController.init(self.__data.candlesController, self.__ticker.getPricePrecision())
        self.__data.rsiController.init(self.__data.candlesController)
        self.__data.divergenceController.init(self.__data.candlesController)
        self.__data.vertexController.init(self.__data.candlesController)
        self.__data.signalController.init(self)

    def __getCandlesAmountForInit(self):
        return self.__data.atrController.getCandlesAmountForInit()

    def isSync(self):
        return self.__data.candlesController.sync()

    def loop(self):
        self.__data.atrController.process()
        self.__data.rsiController.process()
        self.__data.vertexController.process()
        self.__data.divergenceController.process()
        #self.__data.signalController.update(self.__data.candlesController.getLastCandle())

    def getTimeframe(self):
        return self.__data.timeframe
    def getAtrController(self):
        return self.__data.atrController
    def getCandlesController(self):
        return self.__data.candlesController
    def getDivergenceController(self):
        return self.__data.divergenceController
    def getSignalController(self):
        return self.__data.signalController
