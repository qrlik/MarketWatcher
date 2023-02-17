
from api import api
from models import timeframe
from models import candle
from systems import configController
from systems import movingAverageController

class TimeframeController:
    def __init__(self, ticker:str, tf: str):
        self.__averagesController = movingAverageController.MovingAverageController(configController.getMovingAverages(tf))
        self.__timeframe = timeframe.Timeframe[tf]
        self.__ticker = ticker
        self.__requestCandles()
    
    def __requestCandles(self):
        amountForAverages = self.__averagesController.getCandlesAmountForInit()
        candles = api.Spot.getCandelsByAmount(self.__ticker, self.__timeframe, amountForAverages)
        if len(candles) == 0:
            return
        self.__currentCandle = candles[-1]
        candles.pop()
        if len(candles) == 0:
            return
        self.__lastClosedCandle = candles[-1]
        for candle in candles:
            self.__averagesController.process(candle)

    __averagesController: movingAverageController.MovingAverageController = None
    __timeframe: timeframe.Timeframe = None
    __ticker:str = ''
    __lastClosedCandle:candle.Candle = None
    __currentCandle:candle.Candle = None