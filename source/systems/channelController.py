from systems import settingsController
from systems.vertexController import VertexType
from utilities import utils

import sys


class VertexData:
    def __init__(self, index, pivot, close):
        self.index = index
        self.pivot = pivot
        self.close = close

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



class LineFormula: # y = kx + b
    def __init__(self, x1, y1, x2, y2):
        self.__x1 = x1
        self.__y1 = y1
        self.update(x2, y2)

    def update(self, x2, y2):
        self.__k = (y2 - self.__y1) / (x2 - self.__x1) if x2 != self.__x1 else 0
        self.__b = self.__y1 - self.__k * self.__x1

    def comparePoint(self, x, y, functor):
        lineY = self.__k * x + self.__b
        return functor(y, lineY)
    


class LinesData: # data for lines from one vertex (close + pivot) to another
    def __init__(self, firstIndex, firstCandle, isTop):
        pivot = firstCandle.high if isTop else firstCandle.low
        self.firstVertex = VertexData(firstIndex, pivot, firstCandle.close)

        # Extreme Channel Line
        ECL_y = 0.0 if isTop else sys.float_info.max
        self.closeECL = LineFormula(firstIndex, self.firstVertex.close, firstIndex + 1, ECL_y)
        self.pivotECL = LineFormula(firstIndex, self.firstVertex.pivot, firstIndex + 1, ECL_y)

        self.closeToSecondVertexs = [] # VertexData (index growth)
        self.pivotToSecondVertexs = [] # VertexData (index growth)

    def isValid(self):
        return len(self.closeToSecondVertexs) > 0 or len(self.pivotToSecondVertexs) > 0



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
        self.__topLines = [] # LinesData (index growth)
        self.__bottomLines = [] # LinesData (index growth)

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
            topPivotUpdate,topCloseUpdate,bottomPivotUpdate,bottomCloseUpdate = None

            for secondIndex in range(firstIndex + 1, len(self.__candles)):
                secondCandle = self.__candles[secondIndex]
                if topFirstVertex.isPivot:
                    topPivotUpdate = self.__processTwoVertexLines(secondIndex, secondCandle.high, secondCandle.close, topLines.pivotECL, topPivotUpdate, topLines.pivotToSecondVertexs, utils.less)
                if topFirstVertex.isClose:
                    topCloseUpdate = self.__processTwoVertexLines(secondIndex, secondCandle.high, secondCandle.close, topLines.closeECL, topCloseUpdate, topLines.closeToSecondVertexs, utils.less)
                if bottomFirstVertex.isPivot:
                    bottomPivotUpdate = self.__processTwoVertexLines(secondIndex, secondCandle.low, secondCandle.close, bottomLines.pivotECL, bottomPivotUpdate, bottomLines.pivotToSecondVertexs, utils.greater)
                if bottomFirstVertex.isPivot:
                    bottomCloseUpdate = self.__processTwoVertexLines(secondIndex, secondCandle.low, secondCandle.close, bottomLines.closeECL, bottomCloseUpdate, bottomLines.closeToSecondVertexs, utils.greater)
            
            # to do refactor __processTwoVertexLines, a lot of arguments
            # to do update container point by last actual ECL (may be use dirty index to optimize), delete all VertexData pivot and close None

            if topLines.isValid():
                self.__topLines.append(topLines)
            if bottomLines.isValid():
                self.__bottomLines.append(bottomLines)


    def __processTwoVertexLines(self, secondIndex, secondPivotPoint, secondClosePoint, ECL:LineFormula, prevClose, vertexContainer:list, functor):
        updateECL = False
        if prevClose is not None:
            if functor(secondClosePoint, prevClose): # top < | bottom >
                if not ECL.comparePoint(secondIndex, secondClosePoint, functor): # top < (right side) | bottom > (left side)
                    updateECL = True # update at the end to prevent float compare
            else:
                ECL.update(secondIndex - 1, prevClose) # update ECL by previous close

        if ECL.comparePoint(secondIndex, secondPivotPoint, functor): # top < | bottom > | # possible bottleneck (can check only vertexPivot HIGH/LOW)
            return None
        secondVertex = VertexData(secondIndex, secondPivotPoint, None)

        if ECL.comparePoint(secondIndex, secondClosePoint, functor): # top < | bottom > | # possible bottleneck (can check only vertexClose HIGH/LOW)
            vertexContainer.append(secondVertex)
            return None
        secondVertex.close = secondClosePoint
        vertexContainer.append(secondVertex)
        
        if updateECL:
            ECL.update(secondIndex, secondClosePoint)
            return None
        else:
            return secondClosePoint


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
        