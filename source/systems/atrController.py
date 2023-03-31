from models import candle
from systems import settingsController

class AtrController:
    def __init__(self):
        self.__atrs = []
        self.__lastCandle = None
        self.__averageTrueRange = 0.0

    def getAtr(self):
        return self.__averageTrueRange
    
    def getDelta(self):
        return self.__averageTrueRange / self.__lastCandle.close

    def getPrettyDelta(self):
        return round(self.__averageTrueRange / self.__lastCandle.close * 100, 2)

    def getCandlesAmountForInit(self):
        return self.__size * settingsController.getSetting('emaFactor')

    def __calculateTrueRange(self, candle: candle.Candle):
        prevCandle = candle if self.__lastCandle is None else self.__lastCandle
        return max(candle.high, prevCandle.close) - min(candle.low, prevCandle.close)

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
        self.__atrs.append(self.__calculateTrueRange(candle))
        if len(self.__atrs) > self.__size:
            self.__atrs.pop(0)
        self.__lastCandle = candle
        self.__averageTrueRange = self.__calculateAverage()

    __size = settingsController.getSetting('atrAverageLength')
