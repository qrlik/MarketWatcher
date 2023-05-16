
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

    def init(self, tfController):
        self.__candlesController = tfController.getCandlesController()

    def initTest(self, candlesController):
        self.__candlesController = candlesController

    def update(self, candle: candle.Candle):
        if not candle:
            return
        self.__signals.clear()
    
    def getSignals(self):
        return self.__signals
