from models import candle
from models import timeframe
from utilities import utils
from binance.spot import Spot as Spots
from binance.um_futures import UMFutures as Futures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from binance.websocket.spot.websocket_client import SpotWebsocketClient
from datetime import datetime
import os
import socket
import struct
import win32api

class __binanceClient:
    def __init__(self, isSpot:bool):
        self.__socketId = 1
        if isSpot:
            self.__client = Spots(api_key=self.__KEY, api_secret=self.__SECRET)
            self.__websocket = SpotWebsocketClient()
        else:
            self.__client = Futures(key=self.__KEY, secret=self.__SECRET)
            self.__websocket = UMFuturesWebsocketClient()
        self.__websocket.start()

    def exit(self):
        self.__websocket.close()

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
                utcTime = datetime.datetime.utcfromtimestamp(epoch_time)
                win32api.SetSystemTime(utcTime.year, utcTime.month, utcTime.weekday(), utcTime.day, utcTime.hour, utcTime.minute, utcTime.second, 0)
        except socket.timeout as e:
                utils.logError(e)

    def __makeApiCall(self, func, *args):
        while True:
            try:
                return func(*args)
            except Exception as e:
                utils.logError(str(e))
                if hasattr(e, 'error_code') and e.error_code == -1021:
                    self.__updateTime()
                else:
                    return None

    async def __makeApiCallAsync(self, func, *args):
        while True:
            try:
                return await func(*args)
            except Exception as e:
                utils.logError(str(e))
                if hasattr(e, 'error_code') and e.error_code == -1021:
                    self.__updateTime()
                else:
                    return None

    ### sync block
    def getExchangeInfo(self):
        return self.__makeApiCall(self.__client.exchange_info)

    def subscribeKlines(self, ticket, interval: timeframe.Timeframe, callback):
        self.__websocket.kline(symbol=ticket, id=self.__socketId, interval=timeframe.timeframeToApiStr[interval], callback=callback)
        self.__socketId += 1
    ###

    def __parseResponce(self, responceCandles, interval: timeframe.Timeframe):
        c = candle.Candle()
        c.interval = interval
        c.openTime = responceCandles[0]
        c.closeTime = responceCandles[6]
        c.time = datetime.fromtimestamp(responceCandles[0] / 1000).strftime('%H:%M %d-%m')
        c.open = float(responceCandles[1])
        c.high = float(responceCandles[2])
        c.low = float(responceCandles[3])
        c.close = float(responceCandles[4])
        #c.volume = float(responceCandles[5])
        return c

    ### async block
    async def __getCandelsTimed(self, symbol: str, interval: timeframe.Timeframe, amount: int, startPoint: int):
        return await self.__client.klinesAsync(symbol, interval, startTime = startPoint, limit = amount)

    async def __getCandlesByTimestamp(self, symbol: str, interval: timeframe.Timeframe, amount: int, startPoint: int):
        result = []
        intervalStr = timeframe.timeframeToApiStr[interval]
        while amount > 0:
            amountStep = min(amount, self.__maxCandelsAmount)
            result.extend(await self.__getCandelsTimed(symbol, intervalStr, amountStep, startPoint))
            if startPoint == 0:
                startPoint = result[0][0]
                amount = int(utils.floor((utils.getCurrentTime() - result[0][0]) / interval, 0))
            amount -= amountStep
            startPoint = result[-1][0] + interval

        return [self.__parseResponce(responce, interval) for responce in result]

    async def getCandels(self, symbol: str, interval: timeframe.Timeframe, amount: int):
        startPoint = utils.getCurrentTime() - amount * interval
        return await self.__makeApiCallAsync(self.__getCandlesByTimestamp, symbol, interval, amount, startPoint)

    async def getFinishedCandles(self, symbol: str, interval: timeframe.Timeframe, amount: int):
        result = await self.getCandels(symbol, interval, (amount + 1 if amount > 0 else 0))
        if result is not None and len(result) > 0:
            result.pop()
        return result
    ###

    __KEY = os.getenv('BINANCE_KEY')
    __SECRET = os.getenv('BINANCE_SECRET')
    __maxCandelsAmount = 1000

Spot = __binanceClient(True)
Future = __binanceClient(False)

def atExit():
    Spot.exit()
    Future.exit()