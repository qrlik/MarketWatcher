from PySide6.QtCore import QObject
from api import api
from api import apiRequests
from api import stocks
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

    def init(self, ticker, arg, precision:int):
        self.__ticker = ticker
        self.__precision = precision
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
        self.__initDirty = True

    def __requestSync(self):
        if self.__isWaitResponse():
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
        else:
            self.__updateLastCandlesCheck()

    def __updateLastCandlesCheck(self):
        if len(self.__finishedCandles) > 0:
            cacheController.updateLastCandlesCheck(self.__finishedCandles[-1].time, self.__timeframe, self.__ticker)

    def __updateCandles(self, current, finished):
        self.__currentCandle = current
        if finished:
            self.__finishedCandles.append(finished)

    def __isWaitResponse(self):
        return self.__requestId >= 0

    def __checkSyncResponse(self):
        # return True if last finished candle changed
        if not self.__isWaitResponse():
            return False
        response = apiRequests.requester.getResponse(self.__requestId)
        if response is None:
            return False
        self.__requestId = -1

        lastOpenFound = False
        isDirty = False
        startTimestamp = settingsController.getTickerStartTimestamp(self.__ticker)
        if startTimestamp:
            response = [c for c in response if c.closeTime >= startTimestamp]
            
        if len(self.__finishedCandles) == 0:
            lastOpenFound = True
            isDirty = True
            self.__finishedCandles.extend(response)
        else:
            lastOpen = self.__finishedCandles[-1].openTime
            for candle in response:
                if lastOpenFound:
                    isDirty = True
                    self.__finishedCandles.append(candle)
                elif lastOpen == candle.openTime:
                    lastOpenFound = True

        if isDirty:
            self.__currentCandle = None
            if len(self.__finishedCandles) > 0 and workMode.isCrypto():
                self.__currentCandle = self.__finishedCandles.pop()

        self.__shrink()
        self.__updateLastCandlesCheck()
        if not lastOpenFound:
            utils.logError('TimeframeController: ' + self.__ticker + ' ' + self.__timeframe.name + \
            ' sync lastOpen not found - ')
        return isDirty

    def __isCandleAfter(self, afterCandle, beforeCandle):
        return beforeCandle.openTime + beforeCandle.interval == afterCandle.openTime

    def __resync(self):
        utils.log('candlesController resync - ' + self.__ticker + ' ' + self.__timeframe.name)
        self.__requestSync()

    def __syncFromWebsocket(self):
        # return True if last finished candle changed
        if workMode.isStock():
            return False
        data = websocketController.getTickerData(self.__ticker, self.__timeframe)
        currentCandle = data[0]
        finishedCandle = data[1]
        if currentCandle:
            if self.__currentCandle:
                if self.__currentCandle.openTime == currentCandle.openTime:
                    self.__updateCandles(currentCandle, None)
                    return False
                elif finishedCandle and self.__isCandleAfter(currentCandle, self.__currentCandle):
                    self.__updateCandles(currentCandle, finishedCandle)
                    return True
                elif currentCandle.openTime > self.__currentCandle.openTime:
                    self.__resync()
                    return False
                return False
            elif len(self.__finishedCandles) > 0:
                if self.__isCandleAfter(currentCandle, self.__finishedCandles[-1]):
                    self.__updateCandles(currentCandle, None)
                    return False
                elif finishedCandle and self.__isCandleAfter(finishedCandle, self.__finishedCandles[-1]):
                    self.__updateCandles(currentCandle, finishedCandle)
                    return True
                elif currentCandle.openTime > self.__finishedCandles[-1].openTime:
                    self.__resync()
                    return False
                return False
            else:
                self.__updateCandles(currentCandle, finishedCandle)
                return True
        elif finishedCandle:
            if self.__currentCandle:
                if self.__currentCandle.openTime == finishedCandle.openTime:
                    self.__updateCandles(None, finishedCandle)
                    return True
                elif finishedCandle.openTime > self.__currentCandle.openTime:
                    self.__resync()
                    return False
                return False
            elif len(self.__finishedCandles) > 0:
                if self.__isCandleAfter(finishedCandle, self.__finishedCandles[-1]):
                    self.__updateCandles(None, finishedCandle)
                    return True
                elif finishedCandle.openTime > self.__finishedCandles[-1].openTime:
                    self.__resync()
                    return False
                return False
            else:
                self.__updateCandles(None, finishedCandle)
                return True
        return False

    def __shrink(self):
        if len(self.__finishedCandles) > self.__amountForCache:
            self.__finishedCandles = self.__finishedCandles[-self.__amountForCache:]

    def sync(self):
        isDirty = self.__initDirty
        if self.__isWaitResponse():
            isDirty |= self.__checkSyncResponse()
            if not self.__isWaitResponse() and workMode.isStock():
                return isDirty
        if not self.__isWaitResponse():
            isDirty |= self.__syncFromWebsocket()
        return isDirty

    def markClean(self):
        self.__initDirty = False

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

    def getCandlesAmountByOpenTime(self, time):
        amount = 0
        for candle in self.__finishedCandles[::-1]:
            if candle.openTime > time:
                amount += 1
            else:
                break
        return amount

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

    def getPricePrecision(self, price):
        if workMode.isCrypto():
            return self.__precision
        else:
            return stocks.getPricePrecision(price)

    def getLastCandle(self):
        if self.__currentCandle:
            return self.__currentCandle
        if len(self.__finishedCandles) > 0:
            return self.__finishedCandles[-1]
        return None
