from models import candle
from models import timeframe
from utilities import utils
from binance.spot import Spot as Spots
from binance.futures import Futures
from datetime import datetime
import os
import socket
import struct
import win32api

class __binanceClient:
    def __init__(self, isSpot:bool):
        if isSpot:
            self.__client = Spots(key=self.__KEY, secret=self.__SECRET)
        else:
            self.__client = Futures(key=self.__KEY, secret=self.__SECRET)

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
                utils.log(str(e))
                if hasattr(e, 'error_code') and e.error_code == -1021:
                    self.__updateTime()
                else:
                    return None

    def __getCandelsTimed(self, symbol: str, interval: timeframe.Timeframe, amount: int, startPoint: int):
        return self.__client.klines(symbol, interval, startTime = startPoint, limit = amount)

    def __parseResponce(self, responceCandles, interval: timeframe.Timeframe):
        c = candle.Candle()
        c.interval = interval
        c.openTime = responceCandles[0]
        c.closeTime = responceCandles[6]
        c.time = datetime.fromtimestamp(responceCandles[0] / 1000).strftime('%H:%M %d-%m-%Y')
        c.open = float(responceCandles[1])
        c.high = float(responceCandles[2])
        c.low = float(responceCandles[3])
        c.close = float(responceCandles[4])
        c.volume = float(responceCandles[5])
        return c

    def __getCandles(self, symbol: str, interval: timeframe.Timeframe, amount: int, startPoint: int):
        result = []
        intervalStr = timeframe.timeframeToStr[interval]
        startAmount = amount
        while amount > 0:
            amountStep = min(amount, self.__maxCandelsAmount)
            result.extend(self.__getCandelsTimed(symbol, intervalStr, amountStep, startPoint))
            if startPoint == 0:
                startPoint = result[0][0]
                amount = int(utils.floor((utils.getCurrentTime() - result[0][0]) / interval, 0))
                startAmount = amount
            amount -= amountStep
            startPoint = result[-1][0] + interval
            print(int((startAmount - amount) / startAmount * 100))

        return [self.__parseResponce(responce, interval) for responce in result]

    def getCandelsByAmount(self, symbol: str, interval: timeframe.Timeframe, amount: int):
        startPoint = utils.getCurrentTime() - amount * interval
        return self.__makeApiCall(self.__getCandles, symbol, interval, amount, startPoint)

    def getFinishedCandelsByStart(self, symbol: str, interval: timeframe.Timeframe, startPoint: int, amount: int = -1):
        if amount == -1:
            amount = int(utils.floor((utils.getCurrentTime() - startPoint) / interval, 0))
        return self.__makeApiCall(self.__getCandles, symbol, interval, amount, startPoint)

    def getExchangeInfo(self):
        return self.__makeApiCall(self.__client.exchange_info)

    __KEY = os.getenv('BINANCE_KEY')
    __SECRET = os.getenv('BINANCE_SECRET')
    __maxCandelsAmount = 1000
    __client = None

Spot = __binanceClient(True)
Future = __binanceClient(False)
