from enum import Enum
from systems import settingsController

class VertexType(Enum):
    RISE = 0,
    HIGH = 1,
    FALL = 2,
    LOW = 3,
    SAME = 4

class VertexController:
    def __init__(self):
        self.__candleController = None
        self.__strengthLength = 0
        self.__strengthHighs = []
        self.__strengthLows = []
        self.__strengthCloses = []
        for strength in settingsController.getSetting('vertexStrengthToDivergenceLength').keys():
            self.__strengthLength = max(self.__strengthLength, int(strength))
        self.__reset()

    def __reset(self):
        self.__lastOpenTime = 0
        self.__lastCandle = None
        self.__strengthCloses.clear()
        self.__strengthHighs.clear()
        self.__strengthLows.clear()

    def init(self, candleController):
        self.__candleController = candleController

    def __updateStrengthContainer(self, element, container):
        container.append(element)
        if len(container) > self.__strengthLength + 1:
            container.pop(0)

    def __updateCandles(self, candle):
        self.__lastCandle = candle
        self.__lastOpenTime = candle.openTime + candle.interval
        self.__updateStrengthContainer(candle.high, self.__strengthHighs)
        self.__updateStrengthContainer(candle.low, self.__strengthLows)
        self.__updateStrengthContainer(candle.close, self.__strengthCloses)

    def __calculateVertex(self, candle, priceAttrName, vertexAttrName):
        if not self.__lastCandle:
            return None
        candlePrice = getattr(candle, priceAttrName)
        lastCandlePrice = getattr(self.__lastCandle, priceAttrName)
        lastCandleVertex = getattr(self.__lastCandle, vertexAttrName)

        if candlePrice > lastCandlePrice:
            setattr(candle, vertexAttrName, VertexType.HIGH)
            if lastCandleVertex == VertexType.HIGH:
                setattr(self.__lastCandle, vertexAttrName, VertexType.RISE)
        elif candlePrice < lastCandlePrice:
            setattr(candle, vertexAttrName, VertexType.LOW)
            if lastCandleVertex == VertexType.LOW:
                setattr(self.__lastCandle, vertexAttrName, VertexType.FALL)
        else:
            setattr(candle, vertexAttrName, VertexType.SAME)

    def __calculateVertexStrength(self, candle, priceAttrName, vertexAttrName, strengthAttrName, container):
        if not candle:
            return
        vertex = getattr(candle, vertexAttrName)
        if not vertex in [VertexType.HIGH, VertexType.LOW]:
            return
        if len(container) < 2:
            setattr(candle, strengthAttrName, self.__strengthLength)
            return

        curPrice = getattr(candle, priceAttrName)
        for prevPrice in container[-2::-1]: # reverse iterate start from pre-last
            strength = getattr(candle, strengthAttrName)
            if vertex == VertexType.HIGH:
                if prevPrice <= curPrice:
                    setattr(candle, strengthAttrName, strength + 1)
                else:
                    break
            elif vertex == VertexType.LOW:
                if prevPrice >= curPrice:
                    setattr(candle, strengthAttrName, strength + 1)
                else:
                    break
        strength = getattr(candle, strengthAttrName)
        if len(container) < self.__strengthLength and strength + 1 == len(container):
            setattr(candle, strengthAttrName, self.__strengthLength)

    def __processCandleStrength(self, candle):
        self.__calculateVertexStrength(candle, 'high', 'vertexHigh', 'vertexStrengthHigh', self.__strengthHighs)
        self.__calculateVertexStrength(candle, 'low', 'vertexLow', 'vertexStrengthLow', self.__strengthLows)
        self.__calculateVertexStrength(candle, 'close', 'vertexClose', 'vertexStrengthClose', self.__strengthCloses)


    def process(self):
        candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if candles is None:
            self.__reset()
            candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if candles is None:
            return
        
        for candle in candles:
            self.__calculateVertex(candle, 'high', 'vertexHigh')
            self.__calculateVertex(candle, 'low', 'vertexLow')
            self.__calculateVertex(candle, 'close', 'vertexClose')
            self.__processCandleStrength(self.__lastCandle)
            self.__updateCandles(candle)

        self.__processCandleStrength(self.__lastCandle)