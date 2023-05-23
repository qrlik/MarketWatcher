from systems import settingsController
import sys

class RsiController:
    def __init__(self):
        self.__candleController = None
        self.__size = settingsController.getSetting('rsiLength')
        self.__reset()

    def __reset(self):
        self.__counter = 0
        self.__lastOpenTime = 0
        self.__lastCandle = None

    def getCandlesAmountForInit(self):
        return self.__size * settingsController.getSetting('emaFactor')

    def init(self, candleController):
        self.__candleController = candleController

    def setSize(self, size):
        self.__size = size

    def __updateCandles(self,  candle):
        self.__lastCandle = candle
        self.__lastOpenTime = candle.openTime + candle.interval

    def __calculateAverageUp(self, candle, delta):
        if self.__lastCandle is None:
            candle.lastUpMaValue = delta
        else:
            alpha = 1 / self.__size
            candle.lastUpMaValue = alpha * delta + (1 - alpha) * self.__lastCandle.lastUpMaValue
        if self.__counter < self.__size:
            return None
        return candle.lastUpMaValue

    def __calculateAverageDown(self, candle, delta):
        if self.__lastCandle is None:
            candle.lastDownMaValue = delta
        else:
            alpha = 1 / self.__size
            candle.lastDownMaValue = alpha * delta + (1 - alpha) * self.__lastCandle.lastDownMaValue
        if self.__counter < self.__size:
            return None
        return candle.lastDownMaValue

    def __calculateCloseDelta(self, currentCandle):
        lastCandle = currentCandle if self.__lastCandle is None else self.__lastCandle
        return currentCandle.close - lastCandle.close

    def __calculateRSI(self, candle):
        closeDelta = self.__calculateCloseDelta(candle)
        upDelta = closeDelta if closeDelta > 0.0 else 0.0
        downDelta = abs(closeDelta) if closeDelta < 0.0 else 0.0
        self.__counter += 1
        upMa = self.__calculateAverageUp(candle, upDelta)
        downMa = self.__calculateAverageDown(candle, downDelta)
        if not upMa or not downMa:
            return None
        rs = upMa / downMa if downMa > 0.0 else sys.float_info.max
        return 100.0 - 100.0 / (1.0 + rs)

    def process(self):
        candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if candles is None:
            self.__reset()
            candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if candles is None:
            return
        
        for candle in candles:
            rsi = self.__calculateRSI(candle)
            candle.rsi = round(rsi, 2) if rsi else None
            self.__updateCandles(candle)