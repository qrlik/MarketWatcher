from systems.vertexController import VertexType

from enum import IntEnum
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
    def calculateY(self, x):
        return self.__k * x + self.__b
    def getDeltaY(self, x, y):
        line_y = self.__k * x + self.__b
        return abs(line_y - y)

    def comparePoint(self, x, y, functor):
        lineY = self.__k * x + self.__b
        return functor(y, lineY)
    
    @staticmethod
    def getParallelLine(line, delta):
        point1 = (line.getX1(), line.getY1() + delta)
        point2 = (line.getX2(), line.getY2() + delta)
        return LineFormula(point1[0], point1[1], point2[0], point2[1]) 


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


class ZoneComparisonResult(IntEnum):
    DIFFERENT = 0,
    EQUAL = 1,
    GREATER = 2,
    LESS = 3,

class ChannelZone:
    def __init__(self, point, precision = None):
        self.start = point
        self.end = point
        if precision is not None:
            self.precision = precision
            self.precisionStart = self.start
            self.precisionEnd = self.end
            self.__updateRangeWithPrecision()

    def __updateRangeWithPrecision(self):
        actualRange = self.end - self.start
        if actualRange < self.precision:
            delta = int((self.precision - actualRange) / 2)
            self.precisionStart = self.start - delta
            self.precisionEnd = self.end + delta

    def addPoint(self, point, delta):
        if point > self.end:
            if point - self.end <= delta:
                self.end = point
                self.__updateRangeWithPrecision()
                return True
            return False
        return True
    
    def isIntersect(self,zone):
        if zone.precisionStart > self.precisionEnd or self.precisionStart > zone.precisionEnd:
            return False
        return True
    
    def __str__(self):
        if self.start == self.end:
            return str(self.start)
        return '(' + str(self.start) + ',' + str(self.end) + ')'

    @staticmethod
    def zonesetIsIntersect(zoneset1, zoneset2):
        IsFirstLess = len(zoneset1) <= len(zoneset2)
        zoneIteration1 = zoneset1 if IsFirstLess else zoneset2
        zoneIteration2 = zoneset2 if IsFirstLess else zoneset1

        subsetAll = True
        for zone1 in zoneIteration1: # iterate less/equal set
            subset = False
            for zone2 in zoneIteration2:
                if zone1.isIntersect(zone2): # is equal
                    subset = True
                    break
            if not subset:
                subsetAll = False
                break

        if subsetAll:
            if len(zoneset1) == len(zoneset2):
                return ZoneComparisonResult.EQUAL
            if IsFirstLess:
                return ZoneComparisonResult.LESS
            else:
                return ZoneComparisonResult.GREATER
        return ZoneComparisonResult.DIFFERENT



class ChannelProcessData:
    def __init__(self, length, zonePrecisionPercent, line1:LineFormula, point2):
        self.isTop = None
        self.length = length
        self.mainLine = None
        self.secondVertex = None

        self.top = []
        self.bottom = []
        zonePrecision = int(length * zonePrecisionPercent)
        self.zonePrecision = max(zonePrecision, 2)
        self.width = line1.getDeltaY(point2[0], point2[1])

    def __makeZones(self, container):
        if len(container) == 0:
            return []
        zones = [ ChannelZone(container[0], self.zonePrecision) ]
        for point in container[1:]: # start from second
            if not zones[-1].addPoint(point, self.zonePrecision):
                zones.append(ChannelZone(point, self.zonePrecision))
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

        if topResult == bottomResult:
            return topResult
        # to do if both equal comparison by strength
        if topResult == ZoneComparisonResult.EQUAL:
            return bottomResult
        if bottomResult == ZoneComparisonResult.EQUAL:
            return topResult
        
        return ZoneComparisonResult.DIFFERENT
    
class ChannelPoint:
    def __init__(self, index, price, candle):
        self.index = index
        self.price = price
        self.candle = candle

    def __str__(self):
        if self.price is None:
            return str(self.index)
        return '(' + str(self.index) + ',' + str(self.price) + ')'

class Channel:
    def __init__(self):
        self.isTop = None
        self.mainPoint_1:ChannelPoint = None
        self.mainPoint_2:ChannelPoint = None
        self.minorPoint:ChannelPoint = None
        self.topZones = []
        self.bottomZones = []
        self.length = None
        self.width = None
        self.angle = None

    def calculateWidthPercent(self, mainPrice):
        if self.angle >= 0:
            division = mainPrice / self.minorPoint.price if self.isTop else self.minorPoint.price / mainPrice
            assert(division > 1)
            self.width = (division - 1) * 100
        else:
            division = self.minorPoint.price / mainPrice if self.isTop else mainPrice / self.minorPoint.price
            assert(division < 1)
            self.width = (1 - division) * 100

    def __str__(self):
        result = str(self.length) + '\t'
        if self.isTop:
            result += str(self.mainPoint_1) + str(self.mainPoint_2) + ' | '
            result += str(self.minorPoint)
        else:
            result += str(self.minorPoint) + ' | '
            result += str(self.mainPoint_1) + str(self.mainPoint_2)
        result += '\n'
        for zone in self.topZones:
            result += str(zone) + ','
        result += '\n'
        for zone in self.bottomZones:
            result += str(zone) + ','
        result += '\n==============================='
        result += '\n'
        return result


