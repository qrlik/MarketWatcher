from typing import Optional
from PySide6.QtCore import Signal, QObject
from api import api
from models import timeframe
from models import candle
from widgets import asyncHelper
from systems import websocketController
from utilities import utils

class CandlesController(QObject):
    taskDoneSignal = Signal()

    def __init__(self, tf: timeframe.Timeframe):
        super().__init__(None)
        self.__lowestCandleController:CandlesController = None
        self.__requestedCandles:list = None
        self.__finishedCandles:list = []
        self.__lastProcessedOpenTime = 0
        self.__currentCandle:candle.Candle = None

        self.__timeframe:timeframe.Timeframe = tf
        self.__amountForCache = 0
        self.__syncRequested = False
        asyncHelper.Helper.addWorker(self.taskDoneSignal)

    def init(self, ticker, arg, lowestCandleController=None):
        self.__ticker = ticker
        self.__lowestCandleController = lowestCandleController
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

    def __updateCandles(self, current, finished):
        self.__currentCandle = current
        if finished:
            self.__finishedCandles.append(finished)
            self.__shrinkAndSave()

    def __shrinkAndSave(self):
        if len(self.__finishedCandles) > self.__amountForCache:
            self.__finishedCandles = self.__finishedCandles[-self.__amountForCache:]
        self.__checkCandlesSequence()
        forSave = [c for c in self.__finishedCandles]
        if self.__currentCandle:
            forSave.append(self.__currentCandle)
        utils.savePickleJson(self.__getFilename(), forSave)

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

    def __checkSyncResponse(self):
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
        if not lastOpenFound:
            utils.logError('TimeframeController: ' + self.__ticker + ' ' + self.__timeframe.name + \
            ' sync lastOpen not found - ')
        self.__requestedCandles = None
        self.__shrinkAndSave()
        return True

    def __isCandleAfter(self, candle, otherCandle):
        return candle.openTime + candle.interval == otherCandle.openTime

    def __syncFromWebsocket(self):
        data = websocketController.getTickerData(self.__ticker)
        currentCandle = data[0]
        finishedCandle = data[1]
        if currentCandle:
            if self.__currentCandle:
                if self.__currentCandle.openTime == currentCandle.openTime:
                    self.__updateCandles(currentCandle, None)
                    return True
                elif finishedCandle and self.__isCandleAfter(currentCandle, self.__currentCandle):
                    self.__updateCandles(currentCandle, finishedCandle)
                    return True
                elif currentCandle.openTime > self.__currentCandle.openTime:
                    return False
                return True
            elif len(self.__finishedCandles) > 0:
                if self.__isCandleAfter(currentCandle, self.__finishedCandles[-1]):
                    self.__updateCandles(currentCandle, None)
                    return True
                elif finishedCandle and self.__isCandleAfter(finishedCandle, self.__finishedCandles[-1]):
                    self.__updateCandles(currentCandle, finishedCandle)
                    return True
                elif currentCandle.openTime > self.__finishedCandles[-1].openTime:
                    return False
                return True
            else:
                self.__updateCandles(currentCandle, finishedCandle)
                return True
        elif finishedCandle:
            if self.__currentCandle:
                if self.__currentCandle.openTime == finishedCandle.openTime:
                    self.__updateCandles(None, finishedCandle)
                    return True
                elif finishedCandle.openTime > self.__currentCandle.openTime:
                    return False
                return True
            elif len(self.__finishedCandles) > 0:
                if self.__isCandleAfter(finishedCandle, self.__finishedCandles[-1]):
                    self.__updateCandles(None, finishedCandle)
                    return True
                elif finishedCandle.openTime > self.__finishedCandles[-1].openTime:
                    return False
                return True
            else:
                self.__updateCandles(None, finishedCandle)
                return True
        return True

    def __syncFromLowest(self):
        return True

    def sync(self):
        if self.__syncRequested:
            if not self.__checkSyncResponse():
                return False
        result = True
        if self.__lowestCandleController == self:
            result = self.__syncFromWebsocket()
        else:
            result = self.__syncFromLowest()
        if not result:
            self.__requestSync()
        return result

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
