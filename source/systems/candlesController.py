from typing import Optional
from PySide6.QtCore import Signal, QObject
from api import api
from models import timeframe
from models import candle
from widgets import asyncHelper
from utilities import utils

class CandlesController(QObject):
    taskDoneSignal = Signal()

    def __init__(self, tf: timeframe.Timeframe):
        super().__init__(None)
        self.__requestedCandles:list = None
        self.__finishedCandles:list = []
        self.__currentCandle:candle.Candle = None

        self.__amountForCache = 0
        self.__timeframe:timeframe.Timeframe = tf
        asyncHelper.Helper.addWorker(self.taskDoneSignal)

    def init(self, ticker, arg):
        self.__ticker = ticker
        if isinstance(arg, str):
            self.__initTest(arg)
        else:
            self.__initCandles(arg)
    
    def __initTest(self, filename:str):
        candles = utils.loadJsonFile('assets/candles/' + filename)
        self.__finishedCandles =  [candle.createFromDict(c) for c in candles]
    
    def __getFilename(self):
        return utils.cacheFolder + 'tickers/' + self.__ticker + '/' + self.__timeframe.name

    def __initCandles(self, amountForInit):
        self.__amountForCache = amountForInit
        candles = utils.loadPickleJson(self.__getFilename())
        self.__finishedCandles = [] if candles is None else candles
        self.__requestSync()

    def __requestSync(self):
        amountForRequest = self.__amountForCache + 1
        if len(self.__finishedCandles) > 0:
            timeFromLastOpen = utils.getCurrentTime() - self.__finishedCandles[-1].openTime
            amountFromLastOpen = int(timeFromLastOpen / self.__timeframe)
            if amountFromLastOpen >= self.__amountForCache:
                self.__finishedCandles = []
            else:
                amountForRequest = amountFromLastOpen + 1
        asyncHelper.Helper.addTask(self.__requestCandles, amountForRequest)

    async def __requestCandles(self, amountForRequest):
        self.__requestedCandles = await api.Spot.getCandels(self.__ticker, self.__timeframe, amountForRequest)
        self.taskDoneSignal.emit()

    def __sync(self):
        if not self.__requestedCandles:
            return False
        
        lastOpenFound = False
        if len(self.__finishedCandles) == 0:
            lastOpenFound = True
            self.__finishedCandles.extend(self.__requestedCandles)
        else:
            lastOpen = self.__finishedCandles[-1].openTime
            for candle in self.__requestedCandles:
                if lastOpenFound:
                    self.__finishedCandles.append(candle)
                elif lastOpen == candle.openTime:
                    lastOpenFound = True

        if lastOpenFound and len(self.__finishedCandles) > 0:
            self.__currentCandle = self.__finishedCandles.pop()
        self.__requestedCandles = None
        self.__shrinkAndSave()
        return True

    def __shrinkAndSave(self):
        if len(self.__finishedCandles) > self.__amountForCache:
            self.__finishedCandles = self.__finishedCandles[-self.__amountForCache:]
        self.__checkCandlesSequence()
        utils.savePickleJson(self.__getFilename(), self.__finishedCandles)

    def finishInit(self): # to do change to update
        return self.__sync() #to do

    def __checkCandlesSequence(self):
        if len(self.__finishedCandles) == 0:
            return
        lastOpen = self.__finishedCandles[0].openTime
        errorStr = 'TimeframeController: ' + self.__ticker + ' ' + self.__timeframe.name
        if len(self.__finishedCandles) > 1:
            for candle in self.__finishedCandles[1:]:
                if lastOpen + self.__timeframe != candle.openTime:
                    utils.logError(errorStr + ' wrong finish sequence ' + candle.time)
                lastOpen = candle.openTime
        if self.__currentCandle:
            if lastOpen + self.__timeframe != self.__currentCandle.openTime:
                utils.logError(errorStr + ' wrong current sequence ' + self.__currentCandle.time)

    def getFinishedCandles(self):
        return self.__finishedCandles
    
    def getLastCandle(self):
        if self.__currentCandle:
            return self.__currentCandle
        if len(self.__finishedCandles) > 0:
            return self.__finishedCandles[-1]
        return None
