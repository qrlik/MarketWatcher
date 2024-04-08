from systems.vertexController import VertexType

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
        self.__updated = False

    def update(self, x2, y2):
        self.__k = (y2 - self.__y1) / (x2 - self.__x1) if x2 != self.__x1 else 0
        self.__b = self.__y1 - self.__k * self.__x1
        self.__x2 = x2
        self.__y2 = y2
        self.__updated = True

    def isValid(self):
        return self.__updated
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
    def __init__(self):
        self.isTop = None
        self.length = 0
        self.mainLine = None
        self.secondLine = None

        self.top = []
        self.bottom = []
        self.zoneDelta = 0

    def __makeZones(self, container):
        if len(container) == 0:
            return []
        zones = [ ChannelZone(container[0]) ]
        for point in container[1:]: # start from second
            if not zones[-1].addPoint(point, self.zoneDelta):
                zones.append(ChannelZone(point))
        return zones

    def addTopPoint(self, point):
        self.top.append(point)
    def addBottomPoint(self, point):
        self.bottom.append(point)

    def calculateTop(self):
        self.top = sorted(set(self.top))
        self.top = self.__makeZones(self.top)

    def calculateBottom(self):
        self.bottom = sorted(set(self.bottom))
        self.bottom = self.__makeZones(self.bottom)

    def isValidTop(self, minPerSide):
        return len(self.top) >= minPerSide
    
    def isValidBottom(self, minPerSide):
        return len(self.bottom) >= minPerSide
    
    def isValid(self, minPerSide, minForBoth):
        if not self.isValidTop(minPerSide) or not self.isValidBottom(minPerSide):
            return False
        return len(self.top) + len(self.bottom) >= minForBoth
    
    def checkSubzones(self, channel):
        topResult = ChannelZone.zonesetIsIntersect(self.top, channel.top)
        bottomResult = ChannelZone.zonesetIsIntersect(self.bottom, channel.bottom)

        if topResult == bottomResult: # to do more complex compare
            return topResult
        return 0