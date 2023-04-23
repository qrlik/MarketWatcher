
from enum import Enum
from models import candle
from systems import configController
from systems import watcherController

class SignalDirection(Enum):
    NEUTRAL = 0,
    UP = 1,
    DOWN = 2

class SignalController:
    def __init__(self, ticker, averageController, candlesController):
        self.__signals = []
        self.__ticker = ticker
        self.__averageController = averageController
        self.__candlesController = candlesController
        self.__maDeltaController = None

    def setDeltaController(self, arg=None):
        if self.__maDeltaController is not None:
            return
        if not arg:
            tf = configController.getGlobalConfig('maDeltaTimeframe')
            tfController = watcherController.getTicker(self.__ticker).getTimeframe(tf)
            self.__maDeltaController = tfController.getAtrController()
        else:
            self.__maDeltaController = arg

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
        self.setDeltaController()

        delta = self.__maDeltaController.getAtr()
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
