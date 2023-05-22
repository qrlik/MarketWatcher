from enum import Enum

class VertexType(Enum):
    HIGH = 0,
    LOW = 1

class VertexController:
    def __init__(self):
        self.__candleController = None
        self.__reset()

    def __reset(self):
        self.__lastOpenTime = 0
        self.__lastCandle = None

    def init(self, candleController):
        self.__candleController = candleController

    def __updateCandles(self, candle):
        self.__lastCandle = candle
        self.__lastOpenTime = candle.openTime + candle.interval

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