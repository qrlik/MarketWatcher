from systems import cacheController
from systems import settingsController
from systems import vertexController

from collections import OrderedDict
from enum import Enum
import math

class DivergenceType(Enum):
    REGULAR = 0,
    HIDDEN = 1

class DivergenceSignalType(Enum):
    BULL = 0,
    BEAR = 1

class DivergenceInfo:
    def __init__(self):
        self.firstCandle = None
        self.firstIndex = None
        self.secondCandle = None
        self.secondIndex = None
        self.type = None
        self.signal = None
        self.breakPercents = None
        self.breakDelta = None
        self.power = None
        self.finishedWorkedOut = None
        self.viewed = True

class DivergenceController:
    def __init__(self):
        self.__candleController = None
        self.__strengthToLength = OrderedDict(settingsController.getSetting('vertexStrengthToDivergenceLength'))
        self.__maxLength = 0
        for _, length in self.__strengthToLength.items():
            self.__maxLength = max(self.__maxLength, length)
        self.__actualLength = settingsController.getSetting('divergenceActualLength')
        self.__rsiSize = settingsController.getSetting('rsiLength')
        self.__reset()

    def __reset(self):
        self.__candles = []
        self.__lines = OrderedDict()
        self.__divergences = OrderedDict()
        self.__actualsByLength = []
        self.__actuals = []
        self.__lastOpenTime = 0

    def getCandlesAmountForInit(self):
        return self.__maxLength + 1 + self.__actualLength

    def init(self, candleController):
        self.__candleController = candleController

    def setSizes(self, strengthToLength, actual, rsiSize):
        self.__strengthToLength = strengthToLength
        self.__actualLength = actual
        self.__rsiSize = rsiSize

    def __updateCandles(self,  candles):
        self.__candles = candles
        self.__lastOpenTime = candles[0].openTime

    def __processVertexs(self):
        for i in range(len(self.__candles)):
            fromC = self.__candles[i]
            if not fromC.vertex or not fromC.rsi or not fromC.atr:
                continue
            
            isHigh = fromC.vertex == vertexController.VertexType.HIGH
            anglePrice = -math.pi / 2 if isHigh else math.pi / 2
            angleRsi = -math.pi / 2 if isHigh else math.pi / 2
            self.__lines.setdefault(i, [])
            for j in range(i + 1, len(self.__candles)):
                toC = self.__candles[j]
                if fromC.vertex != toC.vertex or not toC.rsi or not toC.atr:
                    continue
                newAnglePrice = math.atan((toC.close - fromC.close) / (j - i))
                newAngleRsi = math.atan((toC.rsi - fromC.rsi) / (j - i))
                isPriceAngleValid = (isHigh and newAnglePrice > anglePrice) or (not isHigh and newAnglePrice < anglePrice)
                isRsiAngleValid = (isHigh and newAngleRsi > angleRsi) or (not isHigh and newAngleRsi < angleRsi)
                if isPriceAngleValid and isRsiAngleValid:
                    self.__lines[i].append(j)
                    anglePrice = newAnglePrice
                    angleRsi = newAngleRsi

    def __checkDivergenceBreakout(self, isHigh, firstCandle, secondCandle):
        isRegularBreakout = False
        isHiddenBreakout = False
        if isHigh:
            if secondCandle.rsi >= firstCandle.rsi:
                isRegularBreakout = True
            if secondCandle.close >= firstCandle.close:
                isHiddenBreakout = True
        else:
            if secondCandle.rsi <= firstCandle.rsi:
                isRegularBreakout = True
            if secondCandle.close <= firstCandle.close:
                isHiddenBreakout = True
        return (isRegularBreakout, isHiddenBreakout)

    def __calculateRegularBreak(self, info: DivergenceInfo):
        rsiToBreak = info.firstCandle.rsi
        rsToBreak = 100 / (100 - rsiToBreak) - 1
        alpha = 1 / self.__rsiSize
        if info.signal == DivergenceSignalType.BEAR: #isHigh
            downMa = (1 - alpha) * info.secondCandle.lastDownMaValue
            upMa = rsToBreak * downMa
            info.breakDelta = (upMa - (1 - alpha) * info.secondCandle.lastUpMaValue) / alpha
        else:
            upMa = (1 - alpha) * info.secondCandle.lastUpMaValue
            downMa = upMa / rsToBreak
            info.breakDelta = (downMa - (1 - alpha) * info.secondCandle.lastDownMaValue) / alpha
        info.breakPercents = info.breakDelta / info.secondCandle.close * 100 + 1

    def __calculatePower(self, info: DivergenceInfo):
        if info.type == DivergenceType.REGULAR:
            self.__calculateRegularBreak(info)
        else:
            info.breakDelta = abs(info.firstCandle.close - info.secondCandle.close)
            info.breakPercents = info.breakDelta / info.secondCandle.close * 100 + 1
        info.power = info.breakDelta / info.secondCandle.atr * info.breakPercents

    def __getDivergenceLength(self, vertexStrength):
        maxLength = self.__maxLength
        for strength, length in self.__strengthToLength.items():
            if vertexStrength >= int(strength):
                maxLength = length
        return maxLength

    def __processDivergences(self):
        for firstVertex, lines in self.__lines.items():
            firstCandle = self.__candles[firstVertex]
            maxLength = self.__getDivergenceLength(firstCandle.vertexStrength)
            isHigh = firstCandle.vertex == vertexController.VertexType.HIGH
            isRegularBreakout = False
            isHiddenBreakout = False
            isFirst = True
            for secondVertex in lines[::-1]:
                secondCandle = self.__candles[secondVertex]
                if isFirst:
                    isRegularBreakout,isHiddenBreakout = self.__checkDivergenceBreakout(isHigh, firstCandle, secondCandle)
                    isFirst = False
                if isRegularBreakout and isHiddenBreakout:
                    break
                
                type = None
                signal = None
                if (secondCandle.close > firstCandle.close) and (secondCandle.rsi < firstCandle.rsi):
                    if isHigh and not isRegularBreakout:
                        type = DivergenceType.REGULAR
                        signal = DivergenceSignalType.BEAR
                    elif not isHigh and not isHiddenBreakout:
                        type = DivergenceType.HIDDEN
                        signal = DivergenceSignalType.BULL
                elif (secondCandle.close < firstCandle.close) and (secondCandle.rsi > firstCandle.rsi):
                    if isHigh and not isHiddenBreakout:
                        type = DivergenceType.HIDDEN
                        signal = DivergenceSignalType.BEAR
                    elif not isHigh and not isRegularBreakout:
                        type = DivergenceType.REGULAR
                        signal = DivergenceSignalType.BULL

                if type and signal:
                    if secondVertex - firstVertex > maxLength:
                        break
                    info = DivergenceInfo()
                    info.firstCandle = firstCandle
                    info.firstIndex = firstVertex
                    info.secondCandle = secondCandle
                    info.secondIndex = secondVertex
                    info.type = type
                    info.signal = signal
                    self.__divergences.setdefault(firstVertex, info)
                    self.__calculatePower(info)
                    break

    def __isCandleWorkedOut(self, divergence, candle):
        if candle is None:
            return False
        price = divergence.secondCandle.close
        atrWorkout = divergence.secondCandle.atr
        isBull = divergence.signal == DivergenceSignalType.BULL
        priceWorkout = price + atrWorkout if isBull else price - atrWorkout
        if (isBull and candle.high >= priceWorkout) \
        or (not isBull and candle.low <= priceWorkout):
            return True
        return False

    def __isDivergenceLengthActual(self, divergence):
        return divergence.secondIndex + self.__actualLength + 1 >= len(self.__candles)

    def __processActualsByLength(self):
        for _, divergence in self.__divergences.items():
            if self.__isDivergenceLengthActual(divergence):
                self.__actualsByLength.append(divergence)
 
    def __isDivergenceWorkedOut(self, divergence):
        if divergence.finishedWorkedOut:
            return True

        if divergence.finishedWorkedOut is None:
            for index in range(divergence.secondIndex + 1, len(self.__candles)):
                if self.__isCandleWorkedOut(divergence, self.__candles[index]):
                    divergence.finishedWorkedOut = True
                    return True
            divergence.finishedWorkedOut = False
        
        return self.__isCandleWorkedOut(divergence, self.__candleController.getCurrentCandle())

    def __processActuals(self):
        self.__actuals.clear()
        for divergence in self.__actualsByLength:
            if not self.__isDivergenceWorkedOut(divergence):
                self.__actuals.append(divergence)
 
    def isEmpty(self):
        return len(self.__actuals) == 0

    def getActuals(self):
        return self.__actuals

    def getPowers(self):
        bullPower = 0.0
        bearPower = 0.0
        for divergence in self.__actuals:
            if divergence.signal == DivergenceSignalType.BULL:
                bullPower += divergence.power
            else:
                bearPower += divergence.power
        return (bullPower, bearPower)

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
            self.__processActuals()
            return

        self.__updateCandles(candles)
        self.__processVertexs()
        self.__processDivergences()
        self.__processActualsByLength()
        self.__processActuals()
        cacheController.updateViewedDivergences(self.__candleController.getTicker(), self.__candleController.getTimeframe().name, self.__actuals)
        