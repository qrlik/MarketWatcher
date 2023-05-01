import os
from collections import OrderedDict

from models import timeframe
from systems import configController
from systems import timeframeController
from utilities import utils

class TickerData:
    def __init__(self, ticker:str, pricePrecision: int):
        self.ticker:str = ticker
        self.pricePrecision:int = pricePrecision
        self.timeframes:OrderedDict = OrderedDict()

class TickerController:
    def __init__(self, ticker:str, pricePrecision: int):
        self.__data = TickerData(ticker,pricePrecision)
        self.__initCacheFolder()

    def init(self):
        self.__initTimeframes()

    def __initCacheFolder(self):
        tickersFolder = utils.cacheFolder + 'tickers'
        if not os.path.exists(tickersFolder):
            os.mkdir(tickersFolder)
        tickerFolder = tickersFolder + '/' + self.__data.ticker
        if not os.path.exists(tickerFolder):
            os.mkdir(tickerFolder)

    def __initTimeframes(self):
        for tf in [timeframe.Timeframe.ONE_MIN]: #configController.getTimeframes():
            tfController = timeframeController.TimeframeController(tf, self)
            self.__data.timeframes.setdefault(tf, tfController)
        for _, tfController in self.__data.timeframes.items():
            tfController.preInit()
    
    def getTicker(self):
        return self.__data.ticker

    def getTimeframes(self):
        return self.__data.timeframes
    
    def getTimeframe(self, tf:timeframe.Timeframe):
        return self.__data.timeframes.get(tf)

    def getPricePrecision(self):
        return self.__data.pricePrecision
    
    def update(self):
        isAllInited = True
        for _, tfController in self.__data.timeframes.items():
            isAllInited &= tfController.finishInit()
        
        if isAllInited:
            for _, tfController in self.__data.timeframes.items():
                tfController.update()
        return isAllInited
