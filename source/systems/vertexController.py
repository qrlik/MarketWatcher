from enum import Enum
from systems import settingsController

class VertexType(Enum):
    RISE = 0,
    HIGH = 1,
    FALL = 2,
    LOW = 3

class VertexController:
    def __init__(self):
        self.__candleController = None
        self.__strengthClosesLength = 0
        self.__strengthCloses = []
        for strength in settingsController.getSetting('vertexStrengthToDivergenceLength').keys():
            self.__strengthClosesLength = max(self.__strengthClosesLength, int(strength))
        self.__reset()

    def __reset(self):
        self.__lastOpenTime = 0
        self.__lastCandle = None
        self.__strengthCloses.clear()

    def init(self, candleController):
        self.__candleController = candleController

    def __updateCandles(self, candle):
        self.__lastCandle = candle
        self.__lastOpenTime = candle.openTime + candle.interval
        self.__strengthCloses.append(candle.close)
        if len(self.__strengthCloses) > self.__strengthClosesLength + 1:
            self.__strengthCloses.pop(0)

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
            setattr(candle, vertexAttrName, lastCandleVertex)
            setattr(self.__lastCandle, vertexAttrName, None)

    def __calculateVertexStrengthClose(self, candle):
        if not candle or len(self.__strengthCloses) < 2:
            return
        if not candle.vertexClose in [VertexType.HIGH, VertexType.LOW]:
            return

        for close in self.__strengthCloses[-2::-1]: # reverse iterate start from pre-last
            if candle.vertexClose == VertexType.HIGH:
                if close <= candle.close:
                    candle.vertexStrengthClose += 1
                else:
                    break
            elif candle.vertexClose == VertexType.LOW:
                if close >= candle.close:
                    candle.vertexStrengthClose += 1
                else:
                    break
        if len(self.__strengthCloses) != self.__strengthClosesLength \
        and candle.vertexStrengthClose == len(self.__strengthCloses):
            candle.vertexStrengthClose = self.__strengthClosesLength

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
            self.__calculateVertexStrengthClose(self.__lastCandle) # calculate for previous
            self.__updateCandles(candle)

        self.__calculateVertexStrengthClose(self.__lastCandle) # calculate for last