from systems import settingsController
from systems.vertexController import VertexType
from utilities import utils

import sys


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

        if candle.vertexClose == VertexType.HIGH: # possible bottleneck (can check only pivots)
            topProcess.isClose = True
            topProcess.isPivot = True
        elif candle.vertexHigh == VertexType.HIGH: # wide bottleneck (can check every pivot)
            topProcess.isPivot = True

        if candle.vertexClose == VertexType.LOW: # possible bottleneck (can check only pivots)
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

class LinesData: # data for lines from one vertex (close + pivot) to another
    def __init__(self, firstIndex, firstCandle, isTop):
        self.firstVertex = VertexData()
        self.firstVertex.index = firstIndex
        self.firstVertex.close = firstCandle.close
        self.firstVertex.pivot = firstCandle.high if isTop else firstCandle.low

        # Extreme Channel Line
        ECL_y = 0.0 if isTop else sys.float_info.max
        self.closeECL = utils.LineFormula(firstIndex, self.firstVertex.close, firstIndex + 1, ECL_y)
        self.pivotECL = utils.LineFormula(firstIndex, self.firstVertex.pivot, firstIndex + 1, ECL_y)

        self.closeToSecondVertex = [] # VertexData (index growth)
        self.pivotToSecondVertex = [] # VertexData (index growth)

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

    def __processLines(self):
        for firstIndex in range(len(self.__candles) - self.__minLength):
            firstCandle = self.__candles[firstIndex]
            topFirstVertex, bottomFirstVertex = VertexProcessData.getProcessData(firstCandle)
            if not topFirstVertex.isValid() and not bottomFirstVertex.isValid():
                continue

            topLines = LinesData(firstIndex, firstCandle, True) if topFirstVertex.isValid() else None
            bottomLines = LinesData(firstIndex, firstCandle, False) if bottomFirstVertex.isValid() else None
            for secondIndex in range(firstIndex + 1, len(self.__candles)):
                secondCandle = self.__candles[secondIndex]
                if topFirstVertex.isPivot:
                    pass # first pivot(high) -> second pivot(high) , close
                if topFirstVertex.isClose:
                    pass # first close -> second pivot(high) , close
                if bottomFirstVertex.isPivot:
                    pass # first pivot(low) -> second pivot(low) , close
                if bottomFirstVertex.isPivot:
                    pass # first pivot(low) -> second pivot(low) , close

    def process(self):
        candles = self.__candleController.getFinishedCandles()
        maxAmount = self.getCandlesAmountForInit()
        if len(candles) > maxAmount:
            candles = candles[-maxAmount:]
        if len(candles) < 3:
            return
        if candles[0].openTime != self.__lastOpenTime:
            self.__reset()
        else:
            return

        self.__updateCandles(candles)

        self.__processLines()

        # self.__processDivergences()
        # self.__processActualsByPowerAndLength()
        # self.__processTricked()
        #cacheController.updateViewedDivergences(self.__candleController.getTicker(), self.__candleController.getTimeframe().name, self.__actuals)
        