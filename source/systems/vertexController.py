from enum import Enum
from systems import settingsController

class VertexType(Enum):
    HIGH = 0,
    LOW = 1

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
        if len(self.__strengthCloses) > self.__strengthClosesLength:
            self.__strengthCloses.pop(0)

    def __calculateVertex(self, candle):
        if not self.__lastCandle:
            return None
        if candle.close > self.__lastCandle.close:
            candle.vertex = VertexType.HIGH
            if self.__lastCandle.vertex == VertexType.HIGH:
                self.__lastCandle.vertex = None
        elif candle.close < self.__lastCandle.close:
            candle.vertex = VertexType.LOW
            if self.__lastCandle.vertex == VertexType.LOW:
                self.__lastCandle.vertex = None
        else:
            candle.vertex = self.__lastCandle.vertex
            self.__lastCandle.vertex = None
        self.__calculateVertexStrength(candle)

    def __calculateVertexStrength(self, candle):
        if candle.vertex is None:
            return
        for close in self.__strengthCloses[::-1]:
            if candle.vertex == VertexType.HIGH:
                if close <= candle.close:
                    candle.vertexStrength += 1
                else:
                    break
            elif candle.vertex == VertexType.LOW:
                if close >= candle.close:
                    candle.vertexStrength += 1
                else:
                    break
        if len(self.__strengthCloses) != self.__strengthClosesLength \
        and candle.vertexStrength == len(self.__strengthCloses):
            candle.vertexStrength = self.__strengthClosesLength

    def process(self):
        candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if candles is None:
            self.__reset()
            candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if candles is None:
            return
        
        for candle in candles:
            self.__calculateVertex(candle)
            self.__updateCandles(candle)