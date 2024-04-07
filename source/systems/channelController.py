from systems import settingsController
from systems.vertexController import VertexType
from utilities import utils

import sys
import math

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
        self.__x2 = x2
        self.__y2 = y2

    def getX1(self):
        return self.__x1
    
    def getY1(self):
        return self.__y1

    def getX2(self):
        return self.__x2
    
    def getY2(self):
        return self.__y2

    def getAngle(self):
        return self.__k

    def comparePoint(self, x, y, functor):
        lineY = self.__k * x + self.__b
        return functor(y, lineY)
    


class LinesData:
    def __init__(self, index, price, ECL_y):
        # Extreme Channel Line (accept any price shadow, and close if it one candle momentum)
        self.ECL = LineFormula(index, price, index + 1, ECL_y)
        self.dirtyLength = 0
        self.linesToSecondVertexs = [] # LineFormula (angle growth - top, angle less - bottom). None is optional

    def cleanupVertexs(self, dirtyFunctor, descending):
        if self.dirtyLength < 1:
            return
        
        acceptedLines = []
        for i in range(len(self.linesToSecondVertexs)):
            line = self.linesToSecondVertexs[i]
            if i >= self.dirtyLength:
                acceptedLines.append(line)
            elif not self.ECL.comparePoint(line.getX2(), line.getY2(), dirtyFunctor): # point is good
                acceptedLines.append(line)

        acceptedLines.sort(key=lambda line : line.getAngle(), reverse=descending)
        self.dirtyLength = 0
        self.linesToSecondVertexs = acceptedLines

class VertexLinesData: # data for lines from one vertex (close + pivot) to another
    def __init__(self, index, candle, isTop):
        pivot = candle.high if isTop else candle.low
        self.firstVertex = VertexData(index, math.log2(pivot), math.log2(candle.close))

        ECL_y = 0.0 if isTop else sys.float_info.max
        self.linesFromClose = LinesData(index, self.firstVertex.close, ECL_y)
        self.linesFromPivot = LinesData(index, self.firstVertex.pivot, ECL_y)

    def isValid(self):
        return len(self.linesFromClose.linesToSecondVertexs) > 0 or len(self.linesFromPivot.linesToSecondVertexs) > 0



class ChannelController:
    __maxLength = settingsController.getSetting('channelMaxLength')
    __minLength = settingsController.getSetting('channelMinLength')

    def init(self, candleController):
        self.__candleController = candleController

    def getCandlesAmountForInit(self):
        return self.__maxLength + 1 # plus 1 because 2 candles make 1 lenght range

    def __init__(self):
        self.__candleController = None
        self.__reset()

    def __reset(self):
        self.__candles = []
        self.__lastOpenTime = 0
        self.__topLines = [] # VertexLinesData (index growth)
        self.__bottomLines = [] # VertexLinesData (index growth)

    def __updateCandles(self,  candles):
        self.__candles = candles
        self.__lastOpenTime = candles[0].openTime


    def __processLines(self):
        for firstIndex in range(len(self.__candles) - self.__minLength):
            firstCandle = self.__candles[firstIndex]
            topFirstVertex, bottomFirstVertex = VertexProcessData.getProcessData(firstCandle)
            if not topFirstVertex.isValid() and not bottomFirstVertex.isValid():
                continue

            # lines data from first vertex to second
            topLines = VertexLinesData(firstIndex, firstCandle, True)
            bottomLines = VertexLinesData(firstIndex, firstCandle, False)
            topPivotUpdate,topCloseUpdate,bottomPivotUpdate,bottomCloseUpdate = None,None,None,None

            for secondIndex in range(firstIndex + 1, len(self.__candles)):
                secondCandle = self.__candles[secondIndex]
                topVertex = VertexData(secondIndex, math.log2(secondCandle.high), math.log2(secondCandle.close))
                bottomVertex = VertexData(secondIndex, math.log2(secondCandle.low), math.log2(secondCandle.close))

                if topFirstVertex.isPivot:
                    topPivotUpdate = self.__processVertexLines(topVertex, topLines.linesFromPivot, topPivotUpdate, utils.less)
                if topFirstVertex.isClose:
                    topCloseUpdate = self.__processVertexLines(topVertex, topLines.linesFromClose, topCloseUpdate, utils.less)
                if bottomFirstVertex.isPivot:
                    bottomPivotUpdate = self.__processVertexLines(bottomVertex, bottomLines.linesFromPivot, bottomPivotUpdate, utils.greater)
                if bottomFirstVertex.isPivot:
                    bottomCloseUpdate = self.__processVertexLines(bottomVertex, bottomLines.linesFromClose, bottomCloseUpdate, utils.greater)
            
            topLines.linesFromPivot.cleanupVertexs(utils.less, False)
            topLines.linesFromClose.cleanupVertexs(utils.less, False)
            bottomLines.linesFromPivot.cleanupVertexs(utils.greater, True)
            bottomLines.linesFromClose.cleanupVertexs(utils.greater, True)

            if topLines.isValid():
                self.__topLines.append(topLines)
            if bottomLines.isValid():
                self.__bottomLines.append(bottomLines)


    def __processVertexLines(self, vertex:VertexData, linesData:LinesData, prevClose, functor):
        ECL = linesData.ECL

        # update ECL by previous close
        updateECL = False
        if prevClose is not None:
            if functor(vertex.close, prevClose): # top < | bottom >
                if not ECL.comparePoint(vertex.index, vertex.close, functor): # top < (right side) | bottom > (left side)
                    updateECL = True # update to new ECL at the end to prevent float compare
            else:
                linesData.dirtyLength = len(linesData.linesToSecondVertexs) - 2 # [0, (prevpivot, prevclose)) dirty
                ECL.update(vertex.index - 1, prevClose)

        # ECL check pivot
        if ECL.comparePoint(vertex.index, vertex.pivot, functor): # top < | bottom > | # possible bottleneck (can check only vertexPivot HIGH/LOW)
            return None
        linesData.linesToSecondVertexs.append(LineFormula(ECL.getX1(), ECL.getY1(), vertex.index, vertex.pivot))

        # ECL check close
        if ECL.comparePoint(vertex.index, vertex.close, functor): # top < | bottom > | # possible bottleneck (can check only vertexClose HIGH/LOW)
            return None
        linesData.linesToSecondVertexs.append(LineFormula(ECL.getX1(), ECL.getY1(), vertex.index, vertex.close))
        
        if updateECL:
            linesData.dirtyLength = len(linesData.linesToSecondVertexs) - 4 # [0, (prevpivot, prevclose)x2) dirty
            ECL.update(vertex.index, vertex.close)
            return None
        else:
            return vertex.close


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

        x = 5

        # self.__processDivergences()
        # self.__processActualsByPowerAndLength()
        # self.__processTricked()
        #cacheController.updateViewedDivergences(self.__candleController.getTicker(), self.__candleController.getTimeframe().name, self.__actuals)
        