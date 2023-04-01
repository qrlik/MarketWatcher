from models import candle
from systems import settingsController
from systems import watcherController

class AtrController:
    def __init__(self, ticker:str):
        self.__atrs = []
        self.__lastCandle = None
        self.__prevCandle = None
        self.__averageTrueRange = 0.0
        self.__ticker = ticker

    def getAtr(self, precision=0):
        ticker = watcherController.getTicker(self.__ticker)
        if ticker:
            precision = ticker.getPricePrecision()
        return round(self.__averageTrueRange, precision)
    
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
        lastValue = self.__averageTrueRange
        if lastValue is None:
            lastValue = self.__atrs[-1]
        else:
            alpha = 2 / (self.__size + 1)
            lastValue = alpha * self.__atrs[-1] + (1 - alpha) * lastValue
        if len(self.__atrs) < self.__size:
            return None
        return lastValue

    def process(self, candle: candle.Candle):
        self.__updateCandles(candle)
        self.__atrs.append(self.__calculateTrueRange())
        if len(self.__atrs) > self.__size:
            self.__atrs.pop(0)
        self.__averageTrueRange = self.__calculateAverage()

    __size = settingsController.getSetting('atrAverageLength')
