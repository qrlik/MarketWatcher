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


class ChannelZone:
    def __init__(self, point):
        self.start = point
        self.end = point
    def addPoint(self, point, delta):
        if point > self.end:
            if point - self.end <= delta:
                self.end = point
                return True
            return False
        return True
    def isIntersect(self,zone):
        if zone.start > self.end or self.start > zone.end:
            return False
        return True

    @staticmethod
    def zonesetIsIntersect(zoneset1, zoneset2):
        #-1 if zoneset1 is subset or equal. zoneset1 <= zoneset2
        # 1 if zoneset1 is superset. zoneset1 > zoneset2
        # 0 if different. zoneset1 != zoneset2

        if zoneset1[-1].end < zoneset2[0].start:
            return 0
        if zoneset2[-1].end < zoneset1[0].start:
            return 0

        IsFirstLess = len(zoneset1) <= len(zoneset2)
        topIteration1 = zoneset1 if IsFirstLess else zoneset2
        topIteration2 = zoneset2 if IsFirstLess else zoneset1

        subsetAll = True
        for zone1 in topIteration1: # iterate less/equal set
            if topIteration2[-1].end < zone1.start:
                return 0
            if zone1.end < topIteration2[0].start:
                return 0

            subset = False
            for zone2 in topIteration2:
                if zone1.isIntersect(zone2): # is equal
                    subset = True
                    break
            if not subset:
                subsetAll = False
                break

        if subsetAll:
            if IsFirstLess: # zoneset1 <= zoneset2
                return -1
            else: # zoneset1 > zoneset2
                return 1
        return 0


class ChannelData:
    def __init__(self, zoneDelta):
        self.top = []
        self.bottom = []
        self.__zoneDelta = zoneDelta

    def __makeZones(self, container):
        if len(container) == 0:
            return []
        zones = [ ChannelZone(container[0]) ]
        for point in container[1:]: # start from second
            if not zones[-1].addPoint(point, self.__zoneDelta):
                zones.append(ChannelZone(point))
        return zones

    def addTopPoint(self, point):
        self.top.append(point)
    def addBottomPoint(self, point):
        self.bottom.append(point)

    def calculate(self):
        self.top = sorted(set(self.top))
        self.bottom = sorted(set(self.bottom))
        self.top = self.__makeZones(self.top)
        self.bottom = self.__makeZones(self.bottom)

    def isValid(self, minPerSide, minForBoth):
        topZones = len(self.top)
        bottomZones = len(self.bottom)
        if topZones < minPerSide or bottomZones < minPerSide:
            return False
        return topZones + bottomZones >= minForBoth
    
    def checkSubzones(self, channel):
        topResult = ChannelZone.zonesetIsIntersect(self.top, channel.top)
        bottomResult = ChannelZone.zonesetIsIntersect(self.bottom, channel.bottom)

        if topResult == bottomResult: # to do more complex compare
            return topResult
        return 0



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
        self.__channels = []

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

    def __processChannels(self):
        self.__processOneSideLinesForChannels(True)
        self.__processOneSideLinesForChannels(False)

    def __processOneSideLinesForChannels(self, isTop):
        firstSide = self.__topLines if isTop else self.__bottomLines
        secondSide = self.__bottomLines if isTop else self.__topLines
        breakFunctor = utils.less if isTop else utils.greater
        approximateFunctor = utils.greater if isTop else utils.less

        for linesVertex1 in firstSide:
            zoneDelta = int((self.__maxLength - linesVertex1.firstVertex.index) * 0.02) # to do settings
            zoneDelta = max(zoneDelta, 2)
            for linesVertex2 in secondSide:
                if linesVertex1.firstVertex.index > linesVertex2.firstVertex.index: # look only right side
                    continue
                self.__processVertexsChannels(linesVertex1.linesFromPivot, linesVertex2.linesFromClose, breakFunctor, approximateFunctor, isTop, zoneDelta)
                self.__processVertexsChannels(linesVertex1.linesFromPivot, linesVertex2.linesFromPivot, breakFunctor, approximateFunctor, isTop, zoneDelta)
                self.__processVertexsChannels(linesVertex1.linesFromClose, linesVertex2.linesFromClose, breakFunctor, approximateFunctor, isTop, zoneDelta)
                self.__processVertexsChannels(linesVertex1.linesFromClose, linesVertex2.linesFromPivot, breakFunctor, approximateFunctor, isTop, zoneDelta)


    def __processVertexsChannels(self, lines1:LinesData, lines2:LinesData, breakFunctor, approximateFunctor, isTop, zoneDelta):
        if len(lines1.linesToSecondVertexs) == 0 or len(lines2.linesToSecondVertexs) == 0:
            return
        
        for line1_i in range(len(lines1.linesToSecondVertexs)):
            line1 = lines1.linesToSecondVertexs[line1_i]
            if breakFunctor(lines2.ECL.getAngle(), line1.getAngle()):
                return
            
            newChannel = ChannelData(zoneDelta)

            newChannel.addTopPoint(line1.getX1()) if isTop else newChannel.addBottomPoint(line1.getX1())
            newChannel.addTopPoint(line1.getX2()) if isTop else newChannel.addBottomPoint(line1.getX2())
            line2_X1 = lines2.linesToSecondVertexs[0].getX1()
            newChannel.addBottomPoint(line2_X1) if isTop else newChannel.addTopPoint(line2_X1)

            for line2_i in range(len(lines2.linesToSecondVertexs)):
                line2 = lines2.linesToSecondVertexs[line2_i]
                if approximateFunctor(line2.getAngle(), line1.getAngle()): # between ECL_2 and line1
                    pass # to do calculate approximate touch side 2
                else:
                    # all prev line1 can be  approximate touch side 1
                    
                    # [this, next lines1] touch side 1
                    for line1_j in range(line1_i + 1, len(lines1.linesToSecondVertexs)):
                        line1_next = lines1.linesToSecondVertexs[line1_j]
                        newChannel.addTopPoint(line1_next.getX2()) if isTop else newChannel.addBottomPoint(line1_next.getX2())

                    # [this, next lines2] - touch side 2
                    newChannel.addBottomPoint(line2.getX2())
                    for line2_j in range(line2_i + 1, len(lines2.linesToSecondVertexs)):
                        line2_next = lines2.linesToSecondVertexs[line2_j]
                        newChannel.addBottomPoint(line2_next.getX2()) if isTop else newChannel.addTopPoint(line2_next.getX2())

            newChannel.calculate()
            if newChannel.isValid(2, 4): # to do make setting
                i = 0
                needAppend = True
                for channel in self.__channels:
                    subsetResult = newChannel.checkSubzones(channel)
                    if subsetResult == 1: # newChannel > channel
                        self.__channels.pop(i)
                        break
                    if subsetResult == -1: # newChannel <= channel
                        needAppend = False
                        break
                    i += 1
                if needAppend:
                    self.__channels.append(newChannel) # newChannel != channels || newChannel > channel
            
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
        self.__processChannels()

        print(len(self.__channels))
        x = 5

        # self.__processDivergences()
        # self.__processActualsByPowerAndLength()
        # self.__processTricked()
        #cacheController.updateViewedDivergences(self.__candleController.getTicker(), self.__candleController.getTimeframe().name, self.__actuals)
        