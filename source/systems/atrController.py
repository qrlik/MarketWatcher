from models import candle
from systems import settingsController
from systems import watcherController

class AtrController:
    def __init__(self, ticker:str):
        self.__size = settingsController.getSetting('atrAverageLength')
        self.__atrs = []
        self.__lastCandle = None
        self.__prevCandle = None
        self.__lastValue = None
        self.__averageTrueRange = None
        self.__customPrecision = 0
        self.__ticker = ticker

    def setSize(self, size):
        self.__size = size

    def setPrecision(self, precision:int):
        self.__customPrecision = precision

    def getAtr(self):
        if self.__averageTrueRange:
            ticker = watcherController.getTicker(self.__ticker)
            if ticker:
                return round(self.__averageTrueRange, ticker.getPricePrecision())
            return round(self.__averageTrueRange, self.__customPrecision)
        return None
    
    def getCandlesAmountForInit(self):
        return self.__size * settingsController.getSetting('emaFactor')

    def __updateCandles(self,  candle: candle.Candle):
        if self.__lastCandle is not None and self.__lastCandle.time != candle.time:
            self.__prevCandle = self.__lastCandle
        self.__lastCandle = candle

    def __calculateTrueRange(self):
        prevCandle = self.__lastCandle if self.__prevCandle is None else self.__prevCandle
        return max(self.__lastCandle.high, prevCandle.close) - min(self.__lastCandle.low, prevCandle.close)

    def __calculateAverage(self):
        if self.__lastValue is None:
            self.__lastValue = self.__atrs[-1]
        else:
            alpha = 2 / (self.__size + 1)
            self.__lastValue = alpha * self.__atrs[-1] + (1 - alpha) * self.__lastValue
        if len(self.__atrs) < self.__size:
            return None
        return self.__lastValue

    def process(self, candle: candle.Candle):
        self.__updateCandles(candle)
        self.__atrs.append(self.__calculateTrueRange())
        if len(self.__atrs) > self.__size:
            self.__atrs.pop(0)
        self.__averageTrueRange = self.__calculateAverage()
