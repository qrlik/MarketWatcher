from systems import settingsController

class AtrController:
    def __init__(self):
        self.__candleController = None
        self.__size = settingsController.getSetting('atrAverageLength')
        self.__reset()

    def init(self, candleController):
        self.__candleController = candleController

    def setSize(self, size):
        self.__size = size

    def getCandlesAmountForInit(self):
        #return self.__size * settingsController.getSetting('emaFactor')
        return self.__size

    def __reset(self):
        self.__lastOpenTime = 0
        self.__lastCandle = None
        self.__lastValue = None
        self.__trueRanges = []

    def __updateCandles(self,  candle):
        self.__lastCandle = candle
        self.__lastOpenTime = candle.openTime + candle.interval

    def __addTrueRange(self, trueRange):
        self.__trueRanges.append(trueRange)
        if len(self.__trueRanges) > self.__size:
            self.__trueRanges.pop(0)

    def __calculateTrueRange(self, currentCandle):
        lastCandle = currentCandle if self.__lastCandle is None else self.__lastCandle
        return max(currentCandle.high, lastCandle.close) - min(currentCandle.low, lastCandle.close)

    def __calculateExpAverage(self):
        if self.__lastValue is None:
            self.__lastValue = self.__trueRanges[-1]
        else:
            #alpha = 2 / (self.__size + 1) #EMA
            alpha = 1 / self.__size #RMA
            self.__lastValue = alpha * self.__trueRanges[-1] + (1 - alpha) * self.__lastValue
        if len(self.__trueRanges) < self.__size:
            return None
        return self.__lastValue

    def __calculateWeightAverage(self):
        weight = 0
        trAndWeightSum = 0.0

        for atr in self.__trueRanges:
            weight += 1
            trAndWeightSum += atr * weight
        return trAndWeightSum / sum(range(weight + 1))

    def process(self):
        candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if candles is None:
            self.__reset()
            candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if candles is None:
            return
        
        for candle in candles:
            self.__addTrueRange(self.__calculateTrueRange(candle))
            #atr = self.__calculateExpAverage() # check for None if uncomment
            atr = self.__calculateWeightAverage()
            candle.atr = round(atr, self.__candleController.getPricePrecision(candle.close)) if atr else None
            self.__updateCandles(candle)
            
