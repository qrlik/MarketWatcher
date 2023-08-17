from api.third_party.binance.spot import Spot as Spots
from api.third_party.binance.um_futures import UMFutures as Futures
from api.third_party.binance.websocket.spot.websocket_client import SpotWebsocketClient
from api.third_party.binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from datetime import datetime
import asyncio
import os
import socket
import struct
import win32api
import time

from api import apiRequests
from api import apiLimits
from models import candle
from models import timeframe
from utilities import utils
from systems import settingsController

def getTickersList():
    infoFutures = Future.getExchangeInfo()
    basesFutures = dict()
    exceptions = settingsController.getSetting('baseAssetsExceptions')
    ignores = settingsController.getSetting('baseAssetsIgnores')
    spotIgnore = settingsController.getSetting('spotSymbolsExceptions')
    for symbol in infoFutures.get('symbols', []):
        name = symbol.get('symbol', '')
        status = symbol.get('status', '')
        baseAsset = symbol.get('baseAsset', '')
        quoteAsset = symbol.get('quoteAsset', '')
        underlyingType = symbol.get('underlyingType', '')
        contractType = symbol.get('contractType', '')

        if status == 'TRADING' and underlyingType == 'COIN' and quoteAsset == 'USDT' and contractType == 'PERPETUAL':
            if baseAsset in ignores:
                continue
            baseAsset = baseAsset.replace('1000', '')
            if exceptions.get(baseAsset, None):
                baseAsset = exceptions.get(baseAsset)
            basesFutures.setdefault(baseAsset, name)

    info = Spot.getExchangeInfo()
    tickers = set()
    basesSpot = set()
    for symbol in info.get('symbols', []):
        name = symbol.get('symbol', None)
        baseAsset = symbol.get('baseAsset', '')
        quoteAsset = symbol.get('quoteAsset', '')
        status = symbol.get('status', '')
        pricePrecision = 0
        pricePrecisionFloat = 1.0

        if status != 'TRADING' or quoteAsset != 'USDT':
            continue

        for filter in symbol.get('filters', {}):
            if filter.get('filterType', '') == 'PRICE_FILTER':
                pricePrecisionFloat = float(filter.get('tickSize', 1.0))
                break

        while pricePrecisionFloat < 1.0:
            pricePrecision += 1
            pricePrecisionFloat *= 10

        for base in basesFutures.keys():
            if baseAsset == base:
                tickers.add((name, basesFutures[base], pricePrecision))
                basesSpot.add(baseAsset)
                break

    diffs = set(basesFutures.keys()).symmetric_difference(basesSpot)
    for spot in spotIgnore:
        diffs.discard(spot)
    if len(diffs) > 0:
        utils.log('watcherController::getTickersList not spot symbols - ' + str(diffs))

    return tickers

class __binanceClient:
    def __init__(self, isSpot:bool):
        self.__socketId = 1
        if isSpot:
            self.__client = Spots(api_key=self.__KEY, api_secret=self.__SECRET, show_limit_usage=True)
            self.__websocket = SpotWebsocketClient()
            self.__websocket.start()
        else:
            self.__client = Futures(key=self.__KEY, secret=self.__SECRET, show_limit_usage=True)
            self.__websocket = UMFuturesWebsocketClient()
            self.__websocket.start()

    def exit(self):
        self.__websocket.close()
        self.__websocket.stop()

    def __updateTime(self):
        TIME1970 = 2208988800
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = bytes('\x1b' + 47 * '\0','utf-8')
        try:
            # Timing out the connection after 5 seconds, if no response received
            client.settimeout(5.0)
            client.sendto(data, ('time.windows.com', 123))
            data, _ = client.recvfrom( 1024 )
            if data:
                epoch_time = struct.unpack('!12I', data)[10]
                epoch_time -= TIME1970
                utcTime = datetime.utcfromtimestamp(epoch_time)
                win32api.SetSystemTime(utcTime.year, utcTime.month, utcTime.weekday(), utcTime.day, utcTime.hour, utcTime.minute, utcTime.second, 0)
        except socket.timeout as e:
                utils.logError(e)

    def __processError(self, e):
        if hasattr(e, 'error_code'):
            if e.error_code == -1021:
                self.__updateTime()
            elif e.status_code == 429 or e.status_code == 418 or e.error_code ==-1003:
                apiLimits.onError(e.error_message)
            elif e.status_code == 403:
                apiLimits.onMaintenance()
            else:
                utils.logError(str(e))
        else:
            utils.logError(str(e))

    def __makeApiCall(self, func, *args):
        result = None
        while result is None:
            if apiLimits.isAllowed():
                try:
                    result = func(*args)
                except Exception as e:
                    self.__processError(e)
            else:
                time.sleep(0.5)
        apiLimits.onResponce(result.get('limit_usage', {}))
        return result.get('data', result)

    async def __makeApiCallAsync(self, func, **kwargs):
        result = None
        while result is None:
            if apiLimits.isAllowed():
                try:
                    result = await func(**kwargs)
                except Exception as e:
                    self.__processError(e)
            else:
                await asyncio.sleep(0.5)
        apiLimits.onResponce(result.get('limit_usage', {}))
        return result.get('data', result)

    ### sync block
    def getExchangeInfo(self):
        return self.__makeApiCall(self.__client.exchange_info)

    def getPositions(self):
        return self.__makeApiCall(self.__client.get_position_risk)

    def getListenKey(self):
        return self.__makeApiCall(self.__client.new_listen_key)['listenKey']

    def subscribePositions(self, callback):
        key = self.getListenKey()
        self.__websocket.user_data(listen_key=key, id=self.__socketId, callback=callback)
        self.__socketId += 1

    def subscribeKlines(self, ticket, interval: timeframe.Timeframe, callback):
        self.__websocket.kline(symbol=ticket, id=self.__socketId, interval=timeframe.tfToBinanceApiStr[interval], callback=callback)
        self.__socketId += 1
    ###

    def __parseResponce(self, responceCandles, interval: timeframe.Timeframe):
        c = candle.Candle()
        c.interval = interval
        c.openTime = responceCandles[0]
        c.closeTime = c.openTime + c.interval - 1
        c.time = candle.getPrettyTime(responceCandles[0], c.interval)
        c.open = float(responceCandles[1])
        c.high = float(responceCandles[2])
        c.low = float(responceCandles[3])
        c.close = float(responceCandles[4])
        #c.volume = float(responceCandles[5])
        return c

    ### async block
    async def __getCandelsTimed(self, symbol: str, interval: timeframe.Timeframe, amount: int, startPoint: int):
        return await self.__makeApiCallAsync(self.__client.klinesAsync, symbol = symbol, interval = interval, startTime = startPoint, limit = amount)

    async def __getCandlesByTimestamp(self, symbol: str, interval: timeframe.Timeframe, amount: int, startPoint: int):
        result = []
        intervalStr = timeframe.tfToBinanceApiStr[interval]
        while amount > 0:
            amountStep = min(amount, self.__maxCandelsAmount)
            result.extend(await self.__getCandelsTimed(symbol, intervalStr, amountStep, startPoint))
            if startPoint == 0:
                startPoint = result[0][0]
                amount = int(utils.floor((utils.getCurrentTime() - result[0][0]) / interval, 0))
            amount -= amountStep
            startPoint = result[-1][0] + interval

        return [self.__parseResponce(responce, interval) for responce in result]

    def getCandlesByTimestamp(self, symbol: str, interval: timeframe.Timeframe, amount: int, startPoint: int):
        return apiRequests.requester.addAsyncRequest(self.__getCandlesByTimestamp, symbol, interval, amount, startPoint)

    def getCandels(self, symbol: str, interval: timeframe.Timeframe, amount: int):
        startPoint = utils.getCurrentTime() - amount * interval
        return apiRequests.requester.addAsyncRequest(self.__getCandlesByTimestamp, symbol, interval, amount, startPoint)
    ###

    # async def getFinishedCandles(self, symbol: str, interval: timeframe.Timeframe, amount: int):
    #     result = await self.getCandels(symbol, interval, (amount + 1 if amount > 0 else 0))
    #     if result is not None and len(result) > 0:
    #         result.pop()
    #     return result

    __KEY = os.getenv('BINANCE_KEY')
    __SECRET = os.getenv('BINANCE_SECRET')
    __maxCandelsAmount = 1000

Spot = None
Future = None

def init():
    global Spot,Future
    Spot = __binanceClient(True)
    Future = __binanceClient(False)

def atExit():
    Spot.exit()
    Future.exit()