import os
from systems import configController
from systems import timeframeController
from utilities import utils

class TickerController:
    def __init__(self, ticker:str):
        self.__ticker = ticker
        self.__timeframes = {}
        self.__initCacheFolder()
        self.__initTimeframes()

    def __initCacheFolder(self):
        tickersFolder = utils.cacheFolder + 'tickers'
        if not os.path.exists(tickersFolder):
            os.mkdir(tickersFolder)
        tickerFolder = tickersFolder + '/' + self.__ticker
        if not os.path.exists(tickerFolder):
            os.mkdir(tickerFolder)

    def __initTimeframes(self):
        for timeframe in configController.getConfigs():
            self.__timeframes.setdefault(timeframe, timeframeController.TimeframeController(self.__ticker, timeframe))

    def getTimeframes(self):
        return self.__timeframes
