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
        self.__requestedCandles:list = None
        self.__finishedCandles:list = []
        self.__currentCandle:candle.Candle = None

        self.__timeframe:timeframe.Timeframe = tf
        self.__amountForCache = 0
        self.__syncRequested = False
        self.__ticker = ''
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
        jsonCandles = utils.loadJsonMsgspecFile(self.__getFilename())
        self.__finishedCandles = [] if jsonCandles is None else [candle.createFromDict(c) for c in jsonCandles]
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

    def __updateCandles(self, current, finished, withSave):
        self.__currentCandle = current
        if finished:
            self.__finishedCandles.append(finished)
        if withSave:
            self.__shrinkAndSave()

    def __shrinkAndSave(self):
        if len(self.__finishedCandles) > self.__amountForCache:
            self.__finishedCandles = self.__finishedCandles[-self.__amountForCache:]
        forSave = [c for c in self.__finishedCandles]
        if self.__currentCandle:
            forSave.append(self.__currentCandle)
        utils.saveJsonMsgspecFile(self.__getFilename(), [candle.toDict(c) for c in forSave])

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

        if lastOpenFound:
            self.__currentCandle = None
            if len(self.__finishedCandles) > 0:
                self.__currentCandle = self.__finishedCandles.pop()

        if not lastOpenFound:
            utils.logError('TimeframeController: ' + self.__ticker + ' ' + self.__timeframe.name + \
            ' sync lastOpen not found - ')
        self.__requestedCandles = None
        self.__shrinkAndSave()
        return True

    def __isCandleAfter(self, afterCandle, beforeCandle):
        return beforeCandle.openTime + beforeCandle.interval == afterCandle.openTime

    def __syncFromWebsocket(self):
        data = websocketController.getTickerData(self.__ticker, self.__timeframe)
        currentCandle = data[0]
        finishedCandle = data[1]
        if currentCandle:
            if self.__currentCandle:
                if self.__currentCandle.openTime == currentCandle.openTime:
                    self.__updateCandles(currentCandle, None, False)
                    return True
                elif finishedCandle and self.__isCandleAfter(currentCandle, self.__currentCandle):
                    self.__updateCandles(currentCandle, finishedCandle, True)
                    return True
                elif currentCandle.openTime > self.__currentCandle.openTime:
                    return False
                return True
            elif len(self.__finishedCandles) > 0:
                if self.__isCandleAfter(currentCandle, self.__finishedCandles[-1]):
                    self.__updateCandles(currentCandle, None, True)
                    return True
                elif finishedCandle and self.__isCandleAfter(finishedCandle, self.__finishedCandles[-1]):
                    self.__updateCandles(currentCandle, finishedCandle, True)
                    return True
                elif currentCandle.openTime > self.__finishedCandles[-1].openTime:
                    return False
                return True
            else:
                self.__updateCandles(currentCandle, finishedCandle, True)
                return True
        elif finishedCandle:
            if self.__currentCandle:
                if self.__currentCandle.openTime == finishedCandle.openTime:
                    self.__updateCandles(None, finishedCandle, False)
                    return True
                elif finishedCandle.openTime > self.__currentCandle.openTime:
                    return False
                return True
            elif len(self.__finishedCandles) > 0:
                if self.__isCandleAfter(finishedCandle, self.__finishedCandles[-1]):
                    self.__updateCandles(None, finishedCandle, True)
                    return True
                elif finishedCandle.openTime > self.__finishedCandles[-1].openTime:
                    return False
                return True
            else:
                self.__updateCandles(None, finishedCandle, True)
                return True
        return True

    def sync(self):
        if self.__syncRequested:
            if not self.__checkSyncResponse():
                return False
        result = self.__syncFromWebsocket()
        if not result:
            utils.log('candlesController resync - ' + self.__ticker + ' ' + self.__timeframe.name)
            self.__requestSync()
        return result

    def getCandlesByOpenTime(self, openTime):
        finished = []
        for candle in self.__finishedCandles[::-1]:
            if candle.openTime >= openTime:
                finished.append(candle)
            else:
                break
        finished.reverse()
        if len(finished) > 0:
            if finished[0].openTime == openTime or openTime == 0:
                return finished
            else:
                return None
        return finished

    def getTicker(self):
        return self.__ticker

    def getTimeframe(self):
        return self.__timeframe

    def getFinishedCandles(self):
        return self.__finishedCandles
    
    def getLastCandle(self):
        if self.__currentCandle:
            return self.__currentCandle
        if len(self.__finishedCandles) > 0:
            return self.__finishedCandles[-1]
        return None
