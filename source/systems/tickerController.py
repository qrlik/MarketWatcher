import os
from collections import OrderedDict

from models import timeframe
from systems import configController
from systems import timeframeController
from widgets.filters import timeframesFilter

class TickerData:
    def __init__(self, ticker:str, futureTicker:str, pricePrecision: int):
        self.ticker:str = ticker
        self.futureTicker:str = futureTicker
        self.pricePrecision:int = pricePrecision
        self.timeframes:OrderedDict = OrderedDict()

class TickerController:
    def __init__(self, ticker:str, futureTicker:str, pricePrecision: int):
        self.__data = TickerData(ticker, futureTicker, pricePrecision)

    def init(self):
        self.__initTimeframes()

    def __initTimeframes(self):
        for tf in configController.getTimeframes():
            tfController = timeframeController.TimeframeController(tf, self)
            self.__data.timeframes.setdefault(tf, tfController)
    
    def getTicker(self):
        return self.__data.ticker

    def getFutureTicker(self):
        return self.__data.futureTicker

    def getTimeframes(self):
        return self.__data.timeframes
    
    def getFilteredTimeframes(self):
        result = {}
        for tf, controller in self.__data.timeframes.items():
            if timeframesFilter.isTfEnabled(tf):
                result.setdefault(tf, controller)
        return result

    def getTimeframe(self, tf:timeframe.Timeframe):
        return self.__data.timeframes.get(tf)

    def getPricePrecision(self):
        return self.__data.pricePrecision
    
    def __isAllTimeframesSync(self):
        result = True
        for _, tfController in self.__data.timeframes.items():
            result &= tfController.isSync()
        return result

    def loop(self):
        if not self.__isAllTimeframesSync():
            return
        for _, tfController in self.__data.timeframes.items():
            tfController.loop()
