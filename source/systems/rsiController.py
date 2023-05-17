from systems import settingsController
import sys

class RsiController:
    def __init__(self):
        self.__candleController = None
        self.__size = settingsController.getSetting('rsiLength')
        self.__reset()

    def __reset(self):
        self.__upDeltas = []
        self.__downDeltas = []
        self.__lastOpenTime = 0
        self.__lastUpValue = None
        self.__lastDownValue = None
        self.__lastCandle = None

    def init(self, candleController):
        self.__candleController = candleController

    def setSize(self, size):
        self.__size = size

    def __updateCandles(self,  candle):
        self.__lastCandle = candle
        self.__lastOpenTime = candle.openTime + candle.interval

    def __addDelta(self, container, delta):
        container.append(delta)
        if len(container) > self.__size:
            container.pop(0)

    def __calculateAverageUp(self):
        if self.__lastUpValue is None:
            self.__lastUpValue = self.__upDeltas[-1]
        else:
            alpha = 1 / self.__size
            self.__lastUpValue = alpha * self.__upDeltas[-1] + (1 - alpha) * self.__lastUpValue
        if len(self.__upDeltas) < self.__size:
            return None
        return self.__lastUpValue

    def __calculateAverageDown(self):
        if self.__lastDownValue is None:
            self.__lastDownValue = self.__downDeltas[-1]
        else:
            alpha = 1 / self.__size
            self.__lastDownValue = alpha * self.__downDeltas[-1] + (1 - alpha) * self.__lastDownValue
        if len(self.__downDeltas) < self.__size:
            return None
        return self.__lastDownValue

    def __calculateCloseDelta(self, currentCandle):
        lastCandle = currentCandle if self.__lastCandle is None else self.__lastCandle
        return currentCandle.close - lastCandle.close

    def __calculateRSI(self, candle):
        closeDelta = self.__calculateCloseDelta(candle)
        upDelta = closeDelta if closeDelta > 0.0 else 0.0
        downDelta = abs(closeDelta) if closeDelta < 0.0 else 0.0
        self.__addDelta(self.__upDeltas, upDelta)
        self.__addDelta(self.__downDeltas, downDelta)
        upMa = self.__calculateAverageUp()
        downMa = self.__calculateAverageDown()
        if not upMa or not downMa:
            return None
        rs = upMa / downMa if downMa > 0.0 else sys.float_info.max
        return 100.0 - 100.0 / (1.0 + rs)

    def process(self):
        candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if not candles:
            self.__reset()
            candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if not candles:
            return
        
        for candle in candles:
            rsi = self.__calculateRSI(candle)
            candle.rsi = round(rsi, 2) if rsi else None
            self.__updateCandles(candle)