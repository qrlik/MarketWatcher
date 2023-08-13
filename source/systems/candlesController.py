from PySide6.QtCore import QObject
from api import api
from api import apiRequests
from models import timeframe
from models import candle
from systems import cacheController
from systems import settingsController
from systems import websocketController
from utilities import utils
from utilities import workMode

class CandlesController(QObject):
    def __init__(self, tf: timeframe.Timeframe):
        super().__init__(None)
        self.__finishedCandles:list = []
        self.__currentCandle:candle.Candle = None

        self.__timeframe:timeframe.Timeframe = tf
        self.__amountForCache = 0
        self.__requestId = -1
        self.__ticker = ''

    def init(self, ticker, arg):
        self.__ticker = ticker
        if isinstance(arg, str):
            self.__initTest(arg)
        else:
            self.__initCandles(arg)
    
    def __initTest(self, filename:str):
        candles = utils.loadJsonFile(utils.assetsFolder + 'candles/' + filename)
        self.__finishedCandles = [candle.fromJson(c, self.__timeframe.name) for c in candles]
    
    def __initCandles(self, amountForInit):
        self.__amountForCache = amountForInit
        self.__finishedCandles = cacheController.getCandles(self.__ticker, self.__timeframe.name)
        if len(self.__finishedCandles) > 0 and workMode.isCrypto():
            self.__currentCandle = self.__finishedCandles.pop()
        self.__requestSync()

    def __requestSync(self):
        if self.__requestId >= 0:
            return
        amountForRequest = self.__amountForCache + 1
        needToRequest = True
        if self.__currentCandle and utils.getCurrentTime() < self.__currentCandle.closeTime:
            amountForRequest = 0
        elif len(self.__finishedCandles) > 0:
            if workMode.isCrypto():
                timeFromLastOpen = utils.getCurrentTime() - self.__finishedCandles[-1].openTime
                amountFromLastOpen = int(timeFromLastOpen / self.__timeframe)
                if amountFromLastOpen >= self.__amountForCache:
                    self.__finishedCandles = []
                else:
                    amountForRequest = amountFromLastOpen + 1
            else:
                needToRequest = api.isExpectNewCandles(self.__finishedCandles[-1].openTime, self.__timeframe)
        if workMode.isCrypto():
            if amountForRequest > 0:
                self.__requestId = api.getCandels(self.__ticker, self.__timeframe, amountForRequest)
        elif needToRequest:
            startPoint = api.getExpectedStartPoint(self.__timeframe, self.__amountForCache)
            if len(self.__finishedCandles) > 0:
                startPoint = self.__finishedCandles[-1].openTime
            self.__requestId = api.getStockCandels(self.__ticker, self.__timeframe, startPoint)

    def __updateCandles(self, current, finished):
        self.__currentCandle = current
        if finished:
            self.__finishedCandles.append(finished)

    def __checkSyncResponse(self):
        if self.__requestId == -1:
            return False
        response = apiRequests.requester.getResponse(self.__requestId)
        if response is None:
            return False
        self.__requestId = -1

        lastOpenFound = False
        startTimestamp = settingsController.getTickerStartTimestamp(self.__ticker)
        if startTimestamp:
            response = [c for c in response if c.closeTime >= startTimestamp]
            
        if len(self.__finishedCandles) == 0:
            lastOpenFound = True
            self.__finishedCandles.extend(response)
        else:
            lastOpen = self.__finishedCandles[-1].openTime
            for candle in response:
                if lastOpenFound:
                    self.__finishedCandles.append(candle)
                elif lastOpen == candle.openTime:
                    lastOpenFound = True

        if lastOpenFound:
            self.__currentCandle = None
            if len(self.__finishedCandles) > 0 and workMode.isCrypto():
                self.__currentCandle = self.__finishedCandles.pop()
        self.__shrink()
        if not lastOpenFound:
            utils.logError('TimeframeController: ' + self.__ticker + ' ' + self.__timeframe.name + \
            ' sync lastOpen not found - ')
        return True

    def __isCandleAfter(self, afterCandle, beforeCandle):
        return beforeCandle.openTime + beforeCandle.interval == afterCandle.openTime

    def __syncFromWebsocket(self):
        if workMode.isStock():
            return True
        data = websocketController.getTickerData(self.__ticker, self.__timeframe)
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

    def __shrink(self):
        if len(self.__finishedCandles) > self.__amountForCache:
            self.__finishedCandles = self.__finishedCandles[-self.__amountForCache:]

    def sync(self):
        if self.__requestId >= 0:
            if not self.__checkSyncResponse():
                return False
        result = self.__syncFromWebsocket()
        if not result:
            utils.log('candlesController resync - ' + self.__ticker + ' ' + self.__timeframe.name)
            self.__requestSync()
        return result

    def getJsonData(self):
        self.__shrink()
        jsonData = []
        if workMode.isCrypto():
            jsonData = [candle.toJson(c) for c in self.__finishedCandles]
        else:
            jsonData = [candle.toSpotJson(c) for c in self.__finishedCandles]
        if self.__currentCandle and workMode.isCrypto():
            jsonData.append(candle.toJson(self.__currentCandle))
        return jsonData

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
    
    def getCurrentCandle(self):
        return self.__currentCandle

    def getLastCandle(self):
        if self.__currentCandle:
            return self.__currentCandle
        if len(self.__finishedCandles) > 0:
            return self.__finishedCandles[-1]
        return None
