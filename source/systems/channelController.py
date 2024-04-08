from systems import settingsController
from utilities import utils
from utilities.channelUtils import VertexData
from utilities.channelUtils import VertexProcessData
from utilities.channelUtils import LineFormula
from utilities.channelUtils import LinesData
from utilities.channelUtils import VertexLinesData
from utilities.channelUtils import ChannelData

import math

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

        channelData = ChannelData()
        for linesVertex1 in firstSide:
            channelData.length = self.__maxLength - linesVertex1.firstVertex.index
            for linesVertex2 in secondSide:
                if linesVertex1.firstVertex.index > linesVertex2.firstVertex.index: # look only right side
                    continue
                self.__processVertexsChannels(channelData, linesVertex1.linesFromPivot, linesVertex2.linesFromClose, breakFunctor, approximateFunctor, isTop)
                self.__processVertexsChannels(channelData, linesVertex1.linesFromPivot, linesVertex2.linesFromPivot, breakFunctor, approximateFunctor, isTop)
                self.__processVertexsChannels(channelData, linesVertex1.linesFromClose, linesVertex2.linesFromClose, breakFunctor, approximateFunctor, isTop)
                self.__processVertexsChannels(channelData, linesVertex1.linesFromClose, linesVertex2.linesFromPivot, breakFunctor, approximateFunctor, isTop)

    def __processVertexsChannels(self, channelData:ChannelData, lines1:LinesData, lines2:LinesData, breakFunctor, approximateFunctor, isTop):
        if len(lines1.linesToSecondVertexs) == 0 or len(lines2.linesToSecondVertexs) == 0:
            return
        for line1_i in range(len(lines1.linesToSecondVertexs)):
            line1 = lines1.linesToSecondVertexs[line1_i]
            if breakFunctor(lines2.ECL.getAngle(), line1.getAngle()):
                return
            
            newChannel = self.__createChannelByFirstSide(channelData, lines1, line1_i, isTop)
            if not newChannel:
                return

            newChannel = self.__processChannelBySecondSide(newChannel, lines2, line1, isTop, approximateFunctor)
            if not newChannel:
                continue

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
                newChannel.isTop = isTop
                newChannel.length = channelData.length
                newChannel.mainLine = line1
                self.__channels.append(newChannel) # newChannel != channels || newChannel > channel
 
    def __createChannelByFirstSide(self, channelData:ChannelData, lines1, index, isTop):
        # create channel and check first side validation (touches amount)
        line1 = lines1.linesToSecondVertexs[index]

        newChannel = ChannelData()
        newChannel.zoneDelta = int((channelData.length) * 0.02) # to do settings
        newChannel.zoneDelta = max(newChannel.zoneDelta, 2)
        
        # to do all prev line1 can be  approximate touch side 1
        # [this, next lines1] touch side 1
        newChannel.addTopPoint(line1.getX1()) if isTop else newChannel.addBottomPoint(line1.getX1())
        newChannel.addTopPoint(line1.getX2()) if isTop else newChannel.addBottomPoint(line1.getX2())
        for line1_j in range(index + 1, len(lines1.linesToSecondVertexs)):
            line1_next = lines1.linesToSecondVertexs[line1_j]
            newChannel.addTopPoint(line1_next.getX2()) if isTop else newChannel.addBottomPoint(line1_next.getX2())
        
        newChannel.calculateTop() if isTop else newChannel.calculateBottom()
        isFirstSideValid = newChannel.isValidTop(2) if isTop else newChannel.isValidBottom(2) # to do make setting
        if not isFirstSideValid:
            return None
        return newChannel

    def __processChannelBySecondSide(self, newChannel:ChannelData, lines2, line1, isTop, approximateFunctor):
        # process channel by second side validation (touches amount and both sides check)
        line2_X1 = lines2.linesToSecondVertexs[0].getX1()
        newChannel.addBottomPoint(line2_X1) if isTop else newChannel.addTopPoint(line2_X1)
        approximatePassed = False
        for line2_i in range(len(lines2.linesToSecondVertexs)):
            line2 = lines2.linesToSecondVertexs[line2_i]
            if approximatePassed: # touch side 2
                newChannel.addBottomPoint(line2.getX2()) if isTop else newChannel.addTopPoint(line2.getX2())
            elif approximateFunctor(line2.getAngle(), line1.getAngle()):
                pass # to do calculate approximate touch side 2
            else:
                newChannel.secondLine = line2
                newChannel.addBottomPoint(line2.getX2()) if isTop else newChannel.addTopPoint(line2.getX2())
                approximatePassed = True

        newChannel.calculateBottom() if isTop else newChannel.calculateTop()
        if not newChannel.isValid(2, 4): # to do make setting
            return None
        return newChannel

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
        # 0.02 -> 0.04 . 82 -> x
        # 2,4 -> 2,5 . 82 -> x
        # 2,4 -> 3,6 . 82 -> x

        # self.__processDivergences()
        # self.__processActualsByPowerAndLength()
        # self.__processTricked()
        #cacheController.updateViewedDivergences(self.__candleController.getTicker(), self.__candleController.getTimeframe().name, self.__actuals)
        