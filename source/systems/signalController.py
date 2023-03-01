
from models import candle
from systems import deltaController
from systems import movingAverageController

class SignalController:
    def __init__(self, timeframeController):
        self.__averageController = timeframeController.getAveragesController()
        self.__deltaController = timeframeController.getDeltaController()

    def update(self, candle: candle.Candle):
        self.__signals.clear()
        delta = self.__deltaController.getDelta()
        for averages, value in self.__averageController.getAverages().items():
            if value is not None:
                topLevel = value + delta
                bottomLevel = value - delta
                if (candle.high >= bottomLevel and candle.high <= topLevel)         \
                    or (candle.low >= bottomLevel and candle.low <= topLevel)       \
                    or (topLevel >= candle.low and topLevel <= candle.high)         \
                    or (bottomLevel >= candle.low and bottomLevel <= candle.high):
                    self.__signals.append(averages)

    __deltaController:deltaController.DeltaController = None
    __averageController:movingAverageController.MovingAverageController = None
    __signals = []