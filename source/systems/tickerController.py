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
        isLowestCandleController = None
        for tf in configController.getTimeframes():
            tfController = timeframeController.TimeframeController(tf, self)
            if not isLowestCandleController:
                isLowestCandleController = tfController.getCandlesController()
            self.__data.timeframes.setdefault(tf, tfController)
        for _, tfController in self.__data.timeframes.items():
            tfController.preInit(isLowestCandleController)
    
    def getTicker(self):
        return self.__data.ticker

    def getTimeframes(self):
        return self.__data.timeframes
    
    def getTimeframe(self, tf:timeframe.Timeframe):
        return self.__data.timeframes.get(tf)

    def getPricePrecision(self):
        return self.__data.pricePrecision
    
    def __isAllTimeframesSync(self):
        result = True
        isFirst = True
        for _, tfController in self.__data.timeframes.items():
            result &= tfController.isSync()
            if isFirst: # wait lowest timeframe sync, then others
                isFirst = False
                if not result:
                    return False
        return result

    def loop(self):
        if not self.__isAllTimeframesSync():
            return
        for _, tfController in self.__data.timeframes.items():
            tfController.loop()
