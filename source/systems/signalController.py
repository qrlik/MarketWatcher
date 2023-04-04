
from enum import Enum
from models import candle
from systems import configController
from systems import watcherController

class SignalDirection(Enum):
    NEUTRAL = 0,
    UP = 1,
    DOWN = 2

class SignalController:
    def __init__(self, ticker, timeframeController):
        self.__signals = []
        self.__ticker = ticker
        self.__averageController = timeframeController.getAveragesController()
        self.__candlesController = timeframeController.getCandlesController()
        self.__maDeltaController = None

    def __getAverageDirection(self, top, botton):
        for candle in self.__candlesController.getFinishedCandles()[-1:]:
            if candle.close > top:
                return SignalDirection.UP
            elif candle.close < botton:
                return SignalDirection.DOWN
        return SignalDirection.NEUTRAL

    def __updateAverages(self, candle: candle.Candle):
        if self.__maDeltaController is None:
            tf = configController.getGlobalConfig('maDeltaTimeframe')
            tfController = watcherController.getTicker(self.__ticker).getTimeframe(tf)
            self.__maDeltaController = tfController.getAtrController()

        delta = self.__maDeltaController.getAtr()
        for average, value in self.__averageController.getAverages().items():
            if value is None:
                continue
            topLevel = value + delta / 2
            bottomLevel = value - delta / 2
            if candle.close <= topLevel and candle.close >= bottomLevel:
                direction = self.__getAverageDirection(topLevel, bottomLevel)
                if direction != SignalDirection.NEUTRAL:
                    self.__signals.append((average, direction))

    def update(self, candle: candle.Candle):
        self.__signals.clear()
        self.__updateAverages(candle)
    
    def getSignals(self):
        return self.__signals
