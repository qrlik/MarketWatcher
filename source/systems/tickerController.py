from collections import OrderedDict

from models import timeframe
from systems import cacheController
from systems import configController
from systems import feeController
from systems import timeframeController
from widgets.filters import timeframesFilter
from utilities import workMode
from utilities import utils

class TickerInfo:
    def __init__(self):
        self.name:str = ''
        self.industry:str = ''
        self.category:str = ''
        self.futureTicker:str = ''

        self.pricePrecision:int = -1

def parseTickerInfo(info):
    result = TickerInfo()
    result.name = info.get('name', '')
    result.industry = info.get('industry', '')
    result.category = info.get('category', '')
    result.futureTicker = info.get('futureTicker', '')
    result.pricePrecision = info.get('pricePrecision', -1)
    return result

class TickerController:
    def __init__(self, ticker:str, info):
        self.__ticker = ticker
        self.__info = parseTickerInfo(info)
        self.__timeframes:OrderedDict = OrderedDict()
        self.__validLastCandle = True
        self.__feeAcceptable = True

    def init(self):
        self.__initTimeframes()

    def __initTimeframes(self):
        for tf in configController.getTimeframes():
            tfController = timeframeController.TimeframeController(tf, self)
            self.__timeframes.setdefault(tf, tfController)
    
    def setInvalidLastCandle(self):
        self.__validLastCandle = False

    def isValidLastCandle(self):
        return self.__validLastCandle

    def isFeeAcceptable(self):
        return self.__feeAcceptable

    def isBored(self):
        return cacheController.getDatestamp(self.__ticker, cacheController.DateStamp.BORED) is not None

    def getTicker(self):
        return self.__ticker

    def getName(self):
        return self.__info.name

    def getIndustry(self):
        return self.__info.industry

    def getCategory(self):
        return self.__info.category

    def getFutureTicker(self):
        return self.__info.futureTicker

    def getTimeframes(self):
        return self.__timeframes
    
    def getFilteredTimeframes(self):
        result = {}
        for tf, controller in self.__timeframes.items():
            if timeframesFilter.isTfEnabled(tf):
                result.setdefault(tf, controller)
        return result

    def getTimeframe(self, tf:timeframe.Timeframe):
        return self.__timeframes.get(tf)

    def getPricePrecision(self):
        if workMode.isCrypto():
            if self.__info.pricePrecision < 0:
                utils.logError('getPricePrecision wrong precision ' + self.__ticker)
                return 0
        return self.__info.pricePrecision

    def loop(self):
        isFirst = True
        for _, tfController in self.__timeframes.items():
            tfController.loop()

            # to do refactor, move feeController inside tfController
            if isFirst:
                lastCandle = tfController.getCandlesController().getLastCandle()
                if lastCandle:
                    self.__feeAcceptable = feeController.isFeeAcceptable(lastCandle.atr)
            isFirst = False
