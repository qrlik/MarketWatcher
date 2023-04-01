from models import movingAverage
from models import candle
from systems import configController
from systems import settingsController

class MovingAverageController:
    def __init__(self, arg):
        if isinstance(arg, list):
            self.__initFromList(arg)
        else:
            self.__initFromTimeframe(arg)

    def __initFromList(self, averages: list):
        self.__lastValues:dict = {}
        self.__closes = []
        self.__averages:dict = {}
        for average in averages:
            self.__averages.setdefault(average)
            self.__lastValues.setdefault(average)
        self.__maxAverageSize = movingAverage.getMaxAverageSize(self.__averages)

    def __initFromTimeframe(self, timeframe: str):
        self.__init__(configController.getTimeframeAverages(timeframe))

    def __calculateSMA(self, amount:int):
        if len(self.__closes) < amount:
            return None
        return sum(self.__closes[-amount:]) / amount

    def __calculateEMA(self, type:movingAverage.MovingAverageType, amount:int):
        lastValue = self.__lastValues.get(type)
        if lastValue is None:
            lastValue = self.__closes[-1]
        else:
            alpha = 2 / (amount + 1)
            lastValue = alpha * self.__closes[-1] + (1 - alpha) * lastValue
        self.__lastValues[type] = lastValue
        if len(self.__closes) < amount:
            return None
        return lastValue

    def __calculateMA(self, type:movingAverage.MovingAverageType):
        averageData = movingAverage.MovingAverageData[type]
        if averageData[1] == movingAverage.MovingAverageMode.SMA:
            self.__averages[type] = self.__calculateSMA(averageData[0])
        elif averageData[1] == movingAverage.MovingAverageMode.EMA:
            self.__averages[type] = self.__calculateEMA(type, averageData[0])

    def process(self, candle: candle.Candle):
        self.__closes.append(candle.close)
        if len(self.__closes) > self.__maxAverageSize:
            self.__closes.pop(0)
        for average in self.__averages.keys():
            self.__calculateMA(average)

    def getAverages(self):
        return self.__averages
    
    def getAverage(self, type:movingAverage.MovingAverageType):
        return self.__averages.get(type, None)

    def getCandlesAmountForInit(self):
        amount = 0
        for average in self.__averages.keys():
            data = movingAverage.MovingAverageData[average]
            if data[1] == movingAverage.MovingAverageMode.SMA:
                amount = max(amount, data[0])
            elif data[1] == movingAverage.MovingAverageMode.EMA:
                amount = max(amount, data[0] * self.__emaFactor)
        return amount

    __emaFactor = settingsController.getSetting('emaFactor')