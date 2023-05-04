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
        self.__lastProcessedOpenTime = 0
        self.__currentCandle:candle.Candle = None

        self.__amountForCache = 0
        self.__syncRequested = False
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
        self.__finishedCandles = [candle.createFromDict(c) for c in candles]
    
    def __getFilename(self):
        return utils.cacheFolder + 'tickers/' + self.__ticker + '/' + self.__timeframe.name

    def __initCandles(self, amountForInit):
        self.__amountForCache = amountForInit
        candles = utils.loadPickleJson(self.__getFilename())
        self.__finishedCandles = [] if candles is None else candles
        if len(self.__finishedCandles) > 0:
            self.__currentCandle = self.__finishedCandles.pop()
        self.__requestSync()

    def __requestSync(self):
        if self.__syncRequested:
            return
        amountForRequest = self.__amountForCache + 1
        if self.__currentCandle and utils.getCurrentTime() < self.__currentCandle.closeTime:
            amountForRequest = 0
        elif len(self.__finishedCandles) > 0:
            timeFromLastOpen = utils.getCurrentTime() - self.__finishedCandles[-1].openTime
            amountFromLastOpen = int(timeFromLastOpen / self.__timeframe)
            if amountFromLastOpen >= self.__amountForCache:
                self.__finishedCandles = []
            else:
                amountForRequest = amountFromLastOpen + 1
        if amountForRequest > 0:
            self.__syncRequested = True
            asyncHelper.Helper.addTask(self.__requestCandles, amountForRequest)

    async def __requestCandles(self, amountForRequest):
        self.__requestedCandles = await api.Spot.getCandels(self.__ticker, self.__timeframe, amountForRequest)
        self.taskDoneSignal.emit() # to do try to move in update

    def __shrinkAndSave(self): # to do think when call this
        if len(self.__finishedCandles) > self.__amountForCache:
            self.__finishedCandles = self.__finishedCandles[-self.__amountForCache:]
        self.__checkCandlesSequence()
        forSave = self.__finishedCandles
        if self.__currentCandle:
            forSave.append(self.__currentCandle)
        utils.savePickleJson(self.__getFilename(), forSave)

    def sync(self):
        if not self.__syncRequested or not self.__requestedCandles:
            return False
        self.__syncRequested = False

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

    def update(self):
        if self.__syncRequested:
            if not self.sync():
                return False
        return True # tmp
        # to do update from websocket
        # не забыть кейс когда большая свеча обновляется после простоя кучей маленьких

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
    
    def getNotProcessedCandles(self):
        result = []
        for candle in self.__finishedCandles:
            if candle.openTime > self.__lastProcessedOpenTime:
                result.append(candle)
        return result

    def markProcessed(self):
        if len(self.__finishedCandles) > 0:
            self.__lastProcessedOpenTime = self.__finishedCandles[-1].openTime

    def getLastCandle(self):
        if self.__currentCandle:
            return self.__currentCandle
        if len(self.__finishedCandles) > 0:
            return self.__finishedCandles[-1]
        return None
