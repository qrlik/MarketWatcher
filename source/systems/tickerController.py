from systems import configController
from systems import timeframeController

class TickerController:
    def __init__(self, ticker:str):
        configController.load('default') #tmp

        self.__ticker = ticker
        self.__initTimeframes()

    def __initTimeframes(self):
        for timeframe in configController.getConfigs():
            self.__timeframes.append(timeframeController.TimeframeController(self.__ticker, timeframe))

    __ticker:str = ''
    __timeframes = []