from systems import settingsController
from utilities import utils
from utilities.channelUtils import VertexData
from utilities.channelUtils import VertexProcessData
from utilities.channelUtils import LineFormula
from utilities.channelUtils import LinesData
from utilities.channelUtils import VertexLinesData
from utilities.channelUtils import Channel
from utilities.channelUtils import ChannelZone
from utilities.channelUtils import ChannelPoint
from utilities.channelUtils import ChannelProcessData
from utilities.channelUtils import ZoneComparisonResult

import math

class ChannelController:
    __maxLength = settingsController.getSetting('channelMaxLength') + 1 # plus 1 because 2 candles make 1 length range
    __minLength = settingsController.getSetting('channelMinLength') + 1
    __oneSideZonesMinimum = settingsController.getSetting('channelOneSideZonesMinimum')
    __firstVertexStrength = settingsController.getSetting('channelFirstVertexStrength')
    __bothSidesZonesMinimum = settingsController.getSetting('channelBothSidesZonesMinimum')
    __zonePrecisionPercent = settingsController.getSetting('channelZonePrecisionPercent')
    __approximateTouchPrecisionPercent = settingsController.getSetting('channelApproximateTouchPrecisionPercent')

    def init(self, candleController):
        self.__candleController = candleController

    def getCandlesAmountForInit(self):
        return self.__maxLength

    def __init__(self):
        self.__candleController = None
        self.__reset()

    def __reset(self):
        self.__candles = []
        self.__lastOpenTime = 0
        self.__topExtremePoints = []
        self.__bottomExtremePoints = []
        self.__topLines = [] # VertexLinesData (index growth)
        self.__bottomLines = [] # VertexLinesData (index growth)
        self.__channels = []

    def __updateCandles(self,  candles):
        self.__candles = candles
        self.__lastOpenTime = candles[0].openTime


    def __processLines(self):
        for firstIndex in range(len(self.__candles) - self.__minLength + 1):
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
            self.__addLines(topLines, bottomLines)

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

    def __addLines(self, topLines, bottomLines):
        if topLines.isValid():
            self.__topLines.append(topLines)

            if len(topLines.linesFromClose.linesToSecondVertexs) > 0:
                self.__topExtremePoints.append((topLines.linesFromClose.ECL.getX2(), topLines.linesFromClose.ECL.getY2())) 
            if len(topLines.linesFromPivot.linesToSecondVertexs) > 0:
                self.__topExtremePoints.append((topLines.linesFromPivot.ECL.getX2(), topLines.linesFromPivot.ECL.getY2()))

        if bottomLines.isValid():
            self.__bottomLines.append(bottomLines)

            if len(bottomLines.linesFromClose.linesToSecondVertexs) > 0:
                self.__bottomExtremePoints.append((bottomLines.linesFromClose.ECL.getX2(), bottomLines.linesFromClose.ECL.getY2())) 
            if len(bottomLines.linesFromPivot.linesToSecondVertexs) > 0:
                self.__bottomExtremePoints.append((bottomLines.linesFromPivot.ECL.getX2(), bottomLines.linesFromPivot.ECL.getY2()))

    def __processExtremePoint(self):
        self.__topExtremePoints = sorted(set(self.__topExtremePoints))
        self.__bottomExtremePoints = sorted(set(self.__bottomExtremePoints))

    def __processChannels(self):
        self.__processOneSideLinesForChannels(True)
        self.__processOneSideLinesForChannels(False)

    def __processOneSideLinesForChannels(self, isTop):
        firstSide = self.__topLines if isTop else self.__bottomLines
        secondSide = self.__bottomLines if isTop else self.__topLines
        breakFunctor = utils.less if isTop else utils.greater
        approximateFunctor = utils.greater if isTop else utils.less

        for linesVertex1 in firstSide:
            pivotAllowByStrength, closeAllowByStrength = VertexProcessData.getStrengthProcessData(self.__candles[linesVertex1.firstVertex.index], self.__firstVertexStrength, isTop)
            if not pivotAllowByStrength and not closeAllowByStrength:
                continue

            channelLength = len(self.__candles) - linesVertex1.firstVertex.index - 1
            for linesVertex2 in secondSide:
                if linesVertex1.firstVertex.index > linesVertex2.firstVertex.index: # look only right side
                    continue
                if pivotAllowByStrength:
                    self.__processVertexsChannels(channelLength, linesVertex1.linesFromPivot, linesVertex2.linesFromClose, breakFunctor, approximateFunctor, isTop)
                    self.__processVertexsChannels(channelLength, linesVertex1.linesFromPivot, linesVertex2.linesFromPivot, breakFunctor, approximateFunctor, isTop)
                if closeAllowByStrength:
                    self.__processVertexsChannels(channelLength, linesVertex1.linesFromClose, linesVertex2.linesFromClose, breakFunctor, approximateFunctor, isTop)
                    self.__processVertexsChannels(channelLength, linesVertex1.linesFromClose, linesVertex2.linesFromPivot, breakFunctor, approximateFunctor, isTop)

    def __processVertexsChannels(self, channelLength, lines1:LinesData, lines2:LinesData, breakFunctor, approximateFunctor, isTop):
        if len(lines1.linesToSecondVertexs) == 0 or len(lines2.linesToSecondVertexs) == 0:
            return
        for line1_i in range(len(lines1.linesToSecondVertexs)):
            line1 = lines1.linesToSecondVertexs[line1_i]
            if breakFunctor(lines2.ECL.getAngle(), line1.getAngle()):
                return
            
            point2 = (lines2.ECL.getX1(), lines2.ECL.getY1())
            newChannel = ChannelProcessData(channelLength, self.__zonePrecisionPercent, line1, point2)
            newChannel.isTop = isTop
            newChannel.mainLine = line1

            newChannel = self.__processChannelByFirstSide(newChannel, lines1, line1_i, isTop)
            if not newChannel:
                return

            newChannel = self.__processChannelBySecondSide(newChannel, lines2, line1, isTop, approximateFunctor)
            if not newChannel:
                continue
            
            needAppend = True
            for channel in self.__channels[:]: # list copy
                subsetResult = newChannel.checkSubzones(channel)
                if subsetResult == ZoneComparisonResult.GREATER:
                    self.__channels.remove(channel)
                elif subsetResult == ZoneComparisonResult.LESS or subsetResult == ZoneComparisonResult.EQUAL:
                    needAppend = False
                    break
            if needAppend:
                self.__channels.append(newChannel)
 
    def __processChannelByFirstSide(self, newChannel:ChannelProcessData, lines1, index, isTop):
        # create channel and check first side validation (touches amount)
        line1 = lines1.linesToSecondVertexs[index]
        aproximateTouchDelta = self.__approximateTouchPrecisionPercent * newChannel.width
        
        newChannel.addTopPoint(line1.getX1()) if isTop else newChannel.addBottomPoint(line1.getX1())
        for line_i in range(len(lines1.linesToSecondVertexs)):
            line = lines1.linesToSecondVertexs[line_i]
            if line_i < index: # previous lines, check aproximate touch
                assert(line1.calculateY(line.getX2()) >= line.getY2() if isTop else line1.calculateY(line.getX2()) <= line.getY2())
                if line1.getDeltaY(line.getX2(), line.getY2()) <= aproximateTouchDelta:
                    newChannel.addTopPoint(line.getX2()) if isTop else newChannel.addBottomPoint(line.getX2())
            else: # crosses
                newChannel.addTopPoint(line.getX2()) if isTop else newChannel.addBottomPoint(line.getX2())

        newChannel.calculateTop() if isTop else newChannel.calculateBottom()
        isFirstSideValid = newChannel.isValidTop(self.__oneSideZonesMinimum) if isTop else newChannel.isValidBottom(self.__oneSideZonesMinimum)
        if not isFirstSideValid:
            return None
        return newChannel

    def __processChannelBySecondSide(self, newChannel:ChannelProcessData, lines2, line1:LineFormula, isTop, approximateFunctor):
        # process channel by second side validation (touches amount and both sides check)
        
        vertex2 = (lines2.ECL.getX1(), lines2.ECL.getY1())
        if not self.__processChannelByLefthandOfSecondSide(isTop, line1, vertex2): 
            return None
        # process righthand lines [v2, channel_end]
        newChannel.secondVertex = vertex2
        newChannel.addBottomPoint(vertex2[0]) if isTop else newChannel.addTopPoint(vertex2[0])

        sign = -1 if isTop else 1
        line2 = LineFormula.getParallelLine(line1, sign * newChannel.width)
        approximatePassed = False
        aproximateTouchDelta = self.__approximateTouchPrecisionPercent * newChannel.width
        for line_i in range(len(lines2.linesToSecondVertexs)):
            line = lines2.linesToSecondVertexs[line_i]
            if approximatePassed: # crosses
                newChannel.addBottomPoint(line.getX2()) if isTop else newChannel.addTopPoint(line.getX2())
            elif approximateFunctor(line.getAngle(), line1.getAngle()): # check aproximate touch
                assert(line2.calculateY(line.getX2()) <= line.getY2() if isTop else line2.calculateY(line.getX2()) >= line.getY2())
                if line2.getDeltaY(line.getX2(), line.getY2()) <= aproximateTouchDelta:
                    newChannel.addBottomPoint(line.getX2()) if isTop else newChannel.addTopPoint(line.getX2())
            else: # crosses
                newChannel.addBottomPoint(line.getX2()) if isTop else newChannel.addTopPoint(line.getX2())
                approximatePassed = True

        newChannel.calculateBottom() if isTop else newChannel.calculateTop()
        if not newChannel.isValid(self.__oneSideZonesMinimum, self.__bothSidesZonesMinimum):
            return None
        return newChannel

    def __processChannelByLefthandOfSecondSide(self, isTop, line1, vertex2): # process left side (channel_start, v2)
        # if isTop second side is bottom
        extremePoints = self.__bottomExtremePoints if isTop else self.__topExtremePoints
        extremeFunctor = utils.greater if isTop else utils.less
        for extreme_i in reversed(range(0, len(extremePoints))):
            extremePoint = extremePoints[extreme_i]
            if extremePoint[0] >= vertex2[0]:
                continue
            if extremePoint[0] <= line1.getX1():
                break
            # to do may be check here touches and approximate touch
            extremeLine = LineFormula(extremePoint[0], extremePoint[1], vertex2[0], vertex2[1])
            if extremeFunctor(extremeLine.getAngle(), line1.getAngle()): # if extreme point beyond channel from left side for second side
                return False
        return True

    def __createReadableInfo(self):
        channels = []
        for channel in self.__channels:
            c = Channel.createFromProcessData(channel, self.__candles)
            channels.append(c)
        self.__channels = channels

    def process(self):
        candles = self.__candleController.getFinishedCandles()
        maxAmount = self.getCandlesAmountForInit()
        if len(candles) > maxAmount:
            candles = candles[-maxAmount:]
        if len(candles) < self.__minLength:
            return
        if candles[0].openTime != self.__lastOpenTime:
            self.__reset()
        else:
            return

        self.__updateCandles(candles)

        self.__processLines()
        self.__processExtremePoint()
        self.__processChannels()

        print(len(self.__channels))
        self.__channels.sort(key=lambda channel : channel.length, reverse=True)

        self.__createReadableInfo()

        for channel in self.__channels:
            print(str(channel))
        x = 5
        # 0.02 -> 0.04 . 82 -> x
        # 2,4 -> 2,5 . 82 -> x
        # 2,4 -> 3,6 . 82 -> x

        # self.__processDivergences()
        # self.__processActualsByPowerAndLength()
        # self.__processTricked()
        #cacheController.updateViewedDivergences(self.__candleController.getTicker(), self.__candleController.getTimeframe().name, self.__actuals)
        