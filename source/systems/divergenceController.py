from widgets.filters import timeframesFilter
from systems import settingsController
from systems import vertexController

from collections import OrderedDict
from enum import Enum
from systems import cacheController
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
        self.tricked = False
        self.viewed = False

    def toDict(self):
        result = {}
        result.setdefault('firstCandle', self.firstCandle.time)
        result.setdefault('secondCandle', self.secondCandle.time)
        result.setdefault('lenght', self.secondIndex - self.firstIndex)
        result.setdefault('type', self.type.name)
        result.setdefault('signal', self.signal.name)
        result.setdefault('power', self.power)
        result.setdefault('break', round(self.breakPercents, 2))
        result.setdefault('tricked', self.tricked)
        return result

class DivergencesPowersInfo:
    def __init__(self):
        self.maxPower = 0.0
        self.bullPower = 0.0
        self.bearPower = 0.0
        self.newBullPower = 0.0
        self.newBearPower = 0.0

class DivergenceController:
    __actualLength = settingsController.getSetting('divergenceActualLength')
    __divergenceTrickedFactor = settingsController.getSetting('divergenceTrickedFactor')
    __rsiSize = settingsController.getSetting('rsiLength')

    def __init__(self):
        self.__candleController = None
        self.__strengthToLength = OrderedDict(settingsController.getSetting('vertexStrengthToDivergenceLength'))
        self.__maxLength = 0
        for _, length in self.__strengthToLength.items():
            self.__maxLength = max(self.__maxLength, length)
        self.__reset()

    def __reset(self):
        self.__candles = []
        self.__lines = OrderedDict()
        self.__divergencesByFirst = OrderedDict()
        self.__divergencesBySecond = OrderedDict()
        self.__actuals = []
        self.__lastOpenTime = 0

    def getCandlesAmountForInit(self):
        return self.__maxLength + 1 + self.__actualLength

    def init(self, candleController):
        self.__candleController = candleController

    def __updateCandles(self,  candles):
        self.__candles = candles
        self.__lastOpenTime = candles[0].openTime

    def __processVertexs(self):
        for i in range(len(self.__candles)):
            fromC = self.__candles[i]
            if not fromC.rsi:
                continue
            if not fromC.vertexClose in [vertexController.VertexType.HIGH, vertexController.VertexType.LOW]:
                continue
            
            self.__lines.setdefault(i, [])
            self.__divergencesByFirst.setdefault(i, [])
            self.__divergencesBySecond.setdefault(i, [])

            isHigh = fromC.vertexClose == vertexController.VertexType.HIGH
            anglePrice = -math.pi / 2 if isHigh else math.pi / 2
            angleRsi = -math.pi / 2 if isHigh else math.pi / 2
            
            for j in range(i + 1, len(self.__candles)):
                toC = self.__candles[j]
                if fromC.vertexClose != toC.vertexClose or not toC.rsi:
                    continue
                newAnglePrice = math.atan((toC.close - fromC.close) / (j - i))
                newAngleRsi = math.atan((toC.rsi - fromC.rsi) / (j - i))
                isPriceAngleValid = (isHigh and newAnglePrice > anglePrice) or (not isHigh and newAnglePrice < anglePrice)
                isRsiAngleValid = (isHigh and newAngleRsi > angleRsi) or (not isHigh and newAngleRsi < angleRsi)
                if isPriceAngleValid and isRsiAngleValid:
                    self.__lines[i].append(j)
                    anglePrice = newAnglePrice
                    angleRsi = newAngleRsi

    def __calculateRegularBreak(self, info: DivergenceInfo):
        rsiToBreak = info.firstCandle.rsi
        rsToBreak = 100 / (100 - rsiToBreak) - 1 if rsiToBreak < 100 else 100
        alpha = 1 / self.__rsiSize
        if info.signal == DivergenceSignalType.BEAR: #isHigh
            downMa = (1 - alpha) * info.secondCandle.lastDownMaValue
            upMa = rsToBreak * downMa
            info.breakDelta = (upMa - (1 - alpha) * info.secondCandle.lastUpMaValue) / alpha
        else:
            upMa = (1 - alpha) * info.secondCandle.lastUpMaValue
            downMa = upMa / rsToBreak
            info.breakDelta = (downMa - (1 - alpha) * info.secondCandle.lastDownMaValue) / alpha
        info.breakPercents = info.breakDelta / info.secondCandle.close * 100

    def __calculatePower(self, info: DivergenceInfo):
        if info.type == DivergenceType.REGULAR:
            self.__calculateRegularBreak(info)
        else:
            info.breakDelta = abs(info.firstCandle.close - info.secondCandle.close)
            info.breakPercents = info.breakDelta / info.secondCandle.close * 100
        info.power = round(info.breakDelta / info.secondCandle.atr, 2) if info.secondCandle.atr is not None else -1.0

    def __getDivergenceLength(self, vertexStrength):
        maxLength = self.__maxLength
        for strength, length in self.__strengthToLength.items():
            if vertexStrength >= int(strength):
                maxLength = length
        return maxLength

    def __processDivergences(self):
        for firstVertex, lines in self.__lines.items():
            firstCandle = self.__candles[firstVertex]
            maxLength = self.__getDivergenceLength(firstCandle.vertexStrengthClose)
            isHigh = firstCandle.vertexClose == vertexController.VertexType.HIGH
            for secondVertex in lines[::-1]:
                secondCandle = self.__candles[secondVertex]
                
                type = None
                signal = None
                if secondCandle.rsi < firstCandle.rsi:
                    if isHigh and secondCandle.close >= firstCandle.close:
                        type = DivergenceType.REGULAR
                        signal = DivergenceSignalType.BEAR
                    elif not isHigh and secondCandle.close > firstCandle.close:
                        type = DivergenceType.HIDDEN
                        signal = DivergenceSignalType.BULL
                elif secondCandle.rsi > firstCandle.rsi:
                    if isHigh and secondCandle.close < firstCandle.close:
                        type = DivergenceType.HIDDEN
                        signal = DivergenceSignalType.BEAR
                    elif not isHigh and secondCandle.close <= firstCandle.close:
                        type = DivergenceType.REGULAR
                        signal = DivergenceSignalType.BULL

                if type and signal:
                    if secondVertex - firstVertex > maxLength:
                        continue
                    info = DivergenceInfo()
                    info.firstCandle = firstCandle
                    info.firstIndex = firstVertex
                    info.secondCandle = secondCandle
                    info.secondIndex = secondVertex
                    info.type = type
                    info.signal = signal
                    self.__divergencesByFirst[firstVertex].append(info)
                    self.__divergencesBySecond[secondVertex].append(info)
                    self.__calculatePower(info)
                    continue

    def __isDivergenceLengthActual(self, divergence):
        return divergence.secondIndex + self.__actualLength + 1 >= len(self.__candles) # plus 1 because 2 candles make 1 lenght range

    def __processActualsByPowerAndLength(self):
        for _, divergences in self.__divergencesByFirst.items():
            if len(divergences) > 0 and self.__isDivergenceLengthActual(divergences[0]):
                self.__actuals.append(divergences[0])
 
    def __processTricked(self):
        for divergence in self.__actuals:
            length = divergence.secondIndex - divergence.firstIndex
            for other in self.__divergencesByFirst[divergence.firstIndex]:
                if divergence.tricked:
                    break
                if divergence == other:
                    continue
                if divergence.signal == other.signal and divergence.type == other.type:
                    otherLength = other.secondIndex - other.firstIndex
                    minLength = int(otherLength * (1 + self.__divergenceTrickedFactor))
                    maxLength = otherLength * 2
                    if length >= minLength and length <= maxLength:
                        divergence.tricked = True
            if divergence.tricked:
                continue
            
            for other in self.__divergencesBySecond[divergence.firstIndex]:
                if divergence.tricked:
                    break
                if divergence == other:
                    continue
                if divergence.signal == other.signal  and divergence.type == other.type:
                    otherLength = other.secondIndex - other.firstIndex
                    minLength = int(otherLength * self.__divergenceTrickedFactor)
                    maxLength = otherLength
                    if length >= minLength and length <= maxLength:
                        divergence.tricked = True

    def isEmpty(self):
        return len(self.__actuals) == 0

    def getActuals(self):
        return self.__actuals

    def getPowers(self, onlyRegulars=False):
        powers = DivergencesPowersInfo()
        for divergence in self.__actuals:
            if onlyRegulars and divergence.type != DivergenceType.REGULAR:
                continue
            if divergence.signal == DivergenceSignalType.BULL:
                powers.maxPower = max(powers.maxPower, divergence.power)
                powers.bullPower += divergence.power
                if not divergence.viewed:
                    powers.newBullPower += divergence.power
            else:
                powers.maxPower = max(powers.maxPower, abs(divergence.power))
                powers.bearPower += divergence.power
                if not divergence.viewed:
                    powers.newBearPower += divergence.power
        return powers
    
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
        self.__processDivergences()
        self.__processActualsByPowerAndLength()
        self.__processTricked()
        cacheController.updateViewedDivergences(self.__candleController.getTicker(), self.__candleController.getTimeframe().name, self.__actuals)
        