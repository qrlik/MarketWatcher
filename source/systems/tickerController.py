import os
from models import timeframe
from systems import configController
from systems import timeframeController
from utilities import utils

class TickerData:
    def __init__(self, ticker:str, pricePrecision: int):
        self.ticker:str = ticker
        self.pricePrecision:int = pricePrecision
        self.timeframes:dict = {}

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
        for timeframe in configController.getTimeframes():
            tfController = timeframeController.TimeframeController(timeframe, self)
            self.__data.timeframes.setdefault(timeframe, tfController)
        for timeframe, tfController in self.__data.timeframes.items():
            tfController.init()
    
    def getTicker(self):
        return self.__data.ticker

    def getTimeframes(self):
        return self.__data.timeframes
    
    def getTimeframe(self, tf:timeframe.Timeframe):
        return self.__data.timeframes.get(tf)

    def getPricePrecision(self):
        return self.__data.pricePrecision
    
    def update(self):
        for _, tfController in self.__data.timeframes.items():
            tfController.update()
