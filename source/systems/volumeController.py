from systems import settingsController
from systems import configController

class VolumeController:
    #__volumeRecheckIntervals = settingsController.getSetting('smallVolumeRecheckIntervals')
    __volumeThreshold = settingsController.getSetting('smallVolumeThresholdMillions')
    __size = settingsController.getSetting('volumeAverageSize')
    
    # @staticmethod
    # def initGlobals():
    #     recheckInterval = []
    #     for factor, interval in VolumeController.__volumeRecheckIntervals.items():
    #         recheckInterval.append((float(factor), interval))
    #     VolumeController.__volumeRecheckIntervals = sorted(recheckInterval)

    # initGlobals()

    def init(self, timeframe, candleController):
        self.__enabled = configController.getConfigState(timeframe, 'VolumeFilter')
        self.__candleController = candleController
        self.__reset()

    def __reset(self):
        self.__lastOpenTime = 0
        self.__volumes = []
        self.__summary = 0
        
    def getCandlesAmountForInit(self):
        return VolumeController.__size
    
    def __updateCandles(self,  candle):
        self.__lastOpenTime = candle.openTime + candle.interval
        
    def __update(self, volume):
        self.__summary += volume
        self.__volumes.append(volume)
        if len(self.__volumes) > self.__size:
            self.__summary -= self.__volumes.pop(0)

    def isValid(self):
        if len(self.__volumes) > 0:
            return self.__summary / len(self.__volumes) >= self.__volumeThreshold
        return False

    def process(self):
        if not self.__enabled:
            return True
        
        candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if candles is None:
            self.__reset()
            candles = self.__candleController.getCandlesByOpenTime(self.__lastOpenTime)
        if candles is None:
            return self.isValid()
        if len(candles) > self.__size:
            candles = candles[-self.__size:]
        
        for candle in candles:
            price = (candle.high + candle.low) / 2
            volumeInMillions = (price * candle.volume) / 1_000_000
            self.__update(volumeInMillions)
            self.__updateCandles(candle)
        
        return self.isValid()
            
        
		
