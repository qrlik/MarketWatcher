from models import movingAverage
from models import candle

class MovingAverageController:
    def __init__(self, averages: list):
        for average in averages:
            self.__averages.setdefault(average)
        self.__maxAverageSize = movingAverage.getMaxAverageSize(self.__averages)

    def __calculateSMA(self, amount:int):
        if len(self.__closes) >= amount:
            return sum(self.__closes[-amount:]) / amount
        return None

    def __calculateEMA(self, lastValue, amount:int):
        if lastValue is None:
            return self.__closes[-1]
        alpha = 2 / (amount + 1)
        return alpha * self.__closes[-1] + (1 - alpha) * lastValue

    def __calculateMA(self, type:movingAverage.MovingAverageType):
        averageData = movingAverage.MovingAverageData[type]
        if averageData[1] == movingAverage.MovingAverageMode.SMA:
            self.__averages[type] = self.__calculateSMA(averageData[0])
        elif averageData[1] == movingAverage.MovingAverageMode.EMA:
            self.__averages[type] = self.__calculateEMA(self.__averages[type], averageData[0])

    def process(self, candle: candle.Candle):
        self.__closes.append(candle.close)
        if len(self.__closes) > self.__maxAverageSize:
            self.__closes.pop(0)
        for average in self.__averages.keys():
            self.__calculateMA(average)

    __averages:dict = {}
    __maxAverageSize = 0
    __closes = []