
from enum import Enum
from models import candle
from models import timeframe
from systems import configController
from systems import watcherController

class SignalDirection(Enum):
    NEUTRAL = 0,
    UP = 1,
    DOWN = 2

class SignalController:
    def __init__(self):
        self.__signals:list = []

    def init(self, tckController, tfController):
        self.__averageController = tfController.getAveragesController()
        self.__candlesController = tfController.getCandlesController()
        deltaTimeframe = timeframe.Timeframe[configController.getGlobalConfig('maDeltaTimeframe')]
        if deltaTimeframe < tfController.getTimeframe():
            self.__deltaController = tckController.getTimeframe(deltaTimeframe).getAtrController()
        else:
            self.__deltaController = tfController.getAtrController()

    def initTest(self, averageController, candlesController, atrController):
        self.__averageController = averageController
        self.__candlesController = candlesController
        self.__deltaController = atrController


    def __getAverageDirection(self, curCandle, top, botton):
        curFound = False
        for candle in self.__candlesController.getFinishedCandles()[::-1]:
            if not curFound:
                if candle.time != curCandle.time:
                    continue
                else:
                    curFound = True

            if candle.close > top:
                return SignalDirection.UP
            elif candle.close < botton:
                return SignalDirection.DOWN
        return SignalDirection.NEUTRAL

    def __updateAverages(self, candle: candle.Candle):
        delta = self.__deltaController.getAtr()
        for average, value in self.__averageController.getAverages().items():
            if value is None or delta is None:
                continue
            topLevel = value + delta / 2
            bottomLevel = value - delta / 2
            if candle.close <= topLevel and candle.close >= bottomLevel:
                direction = self.__getAverageDirection(candle, topLevel, bottomLevel)
                if direction != SignalDirection.NEUTRAL:
                    self.__signals.append((average, direction))

    def update(self, candle: candle.Candle):
        self.__signals.clear()
        self.__updateAverages(candle)
    
    def getSignals(self):
        return self.__signals
