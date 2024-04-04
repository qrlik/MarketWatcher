from systems import settingsController
from systems.vertexController import VertexType

from collections import OrderedDict



class VertexProcessData:
    def __init__(self):
        self.isClose = False
        self.isPivot = False
    
    def isValid(self):
        return self.isClose or self.isPivot
    
    @staticmethod
    def getProcessData(candle):
        topProcess = VertexProcessData()
        bottomProcess = VertexProcessData()

        if candle.vertexClose == VertexType.HIGH:
            topProcess.isClose = True
            topProcess.isPivot = True
        elif candle.vertexHigh == VertexType.HIGH: # wide bottleneck (can check every pivot)
            topProcess.isPivot = True

        if candle.vertexClose == VertexType.LOW:
            bottomProcess.isClose = True
            bottomProcess.isPivot = True
        elif candle.vertexLow == VertexType.LOW: # wide bottleneck
            bottomProcess.isPivot = True

        return (topProcess, bottomProcess)

class VertexData:
    def __init__(self):
        self.index = -1
        self.pivot = 0.0
        self.close = 0.0

class LineData:
    def __init__(self):
        self.firstVertex = VertexData()
        self.closeToSecondVertex = [] # VertexData (index growth)
        self.closeECL = None # TO DO struct
        self.pivotToSecondVertex = [] # VertexData (index growth)
        self.pivotECL = None # TO DO struct

class ChannelController:
    __maxLength = settingsController.getSetting('channelMaxLength')
    __minLength = settingsController.getSetting('channelMinLength')

    def init(self, candleController):
        self.__candleController = candleController

    def getCandlesAmountForInit(self):
        return self.__maxLength + 1 # plus 1 because 2 candles make 1 lenght range

    def __init__(self):
        self.__candleController = None

    def __reset(self):
        self.__candles = []
        self.__lastOpenTime = 0
        self.__topLines = [] # LineData (index growth)
        self.__bottomLines = [] # LineData (index growth)

    def __updateCandles(self,  candles):
        self.__candles = candles
        self.__lastOpenTime = candles[0].openTime

    def __processVertexs(self):
        for firstIndex in range(len(self.__candles)):
            firstCandle = self.__candles[firstIndex]
            topProcess, bottomProcess = VertexProcessData.getProcessData(firstCandle)
            if not topProcess.isValid() and bottomProcess.isValid():
                continue

            for secondIndex in range(firstIndex + 1, len(self.__candles)):
                pass

    def process(self):
        candles = self.__candleController.getFinishedCandles()
        maxAmount = self.getCandlesAmountForInit()
        if len(candles) > maxAmount:
            candles = candles[-maxAmount:]
        elif len(candles) == 0:
            return
        if candles[0].openTime != self.__lastOpenTime:
            self.__reset()
        else:
            return

        self.__updateCandles(candles)

        self.__processVertexs()

        # self.__processDivergences()
        # self.__processActualsByPowerAndLength()
        # self.__processTricked()
        #cacheController.updateViewedDivergences(self.__candleController.getTicker(), self.__candleController.getTimeframe().name, self.__actuals)
        