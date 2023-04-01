
from models import candle
from systems import configController
from systems import watcherController


class SignalController:
    def __init__(self, ticker, averageController):
        self.__signals = []
        self.__averageController = averageController

        tf = configController.getGlobalConfig('maDeltaTimeframe')
        tfController = watcherController.getTicker(ticker).getTimeframe(tf)
        self.__atrController = tfController.getAtrController()
        x = 5

    def update(self, candle: candle.Candle):
        self.__signals.clear()
        delta = self.__atrController.getDelta()
        for average, value in self.__averageController.getAverages().items():
            if value is not None:
                topLevel = value * (1 + delta)
                bottomLevel = value * (1 - delta)
                if (candle.high >= bottomLevel and candle.high <= topLevel)         \
                    or (candle.low >= bottomLevel and candle.low <= topLevel)       \
                    or (topLevel >= candle.low and topLevel <= candle.high)         \
                    or (bottomLevel >= candle.low and bottomLevel <= candle.high):
                    self.__signals.append(average)

    def getSignals(self):
        return self.__signals
