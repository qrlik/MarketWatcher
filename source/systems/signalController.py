
from models import candle
from systems import configController
from systems import watcherController


class SignalController:
    def __init__(self, ticker, averageController):
        self.__signals = []
        self.__ticker = ticker
        self.__averageController = averageController
        self.__maDeltaController = None

    def __updateAverages(self, candle: candle.Candle):
        if self.__maDeltaController is None:
            tf = configController.getGlobalConfig('maDeltaTimeframe')
            tfController = watcherController.getTicker(self.__ticker).getTimeframe(tf)
            self.__maDeltaController = tfController.getAtrController()

        delta = self.__maDeltaController.getAtr()
        for average, value in self.__averageController.getAverages().items():
            if value is not None:
                topLevel = value + delta
                bottomLevel = value - delta
                if (candle.high >= bottomLevel and candle.high <= topLevel)         \
                    or (candle.low >= bottomLevel and candle.low <= topLevel)       \
                    or (topLevel >= candle.low and topLevel <= candle.high)         \
                    or (bottomLevel >= candle.low and bottomLevel <= candle.high):
                    self.__signals.append(average)

    def update(self, candle: candle.Candle):
        self.__signals.clear()
        self.__updateAverages(candle)
    
    def getSignals(self):
        return self.__signals
