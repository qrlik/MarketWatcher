from api import candles
from utilities import utils
from binance.futures import Futures
from datetime import datetime
import os
import socket
import struct
import win32api

__KEY = os.getenv('BINANCE_KEY')
__SECRET = os.getenv('BINANCE_SECRET')
__client = Futures(key=__KEY, secret=__SECRET)
__maxCandelsAmount = 1000

def __updateTime():
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

def __makeApiCall(func):
    while True:
        try:
            return func()
        except Exception as e:
            utils.log(str(e))
            if hasattr(e, 'error_code') and e.error_code == -1021:
                __updateTime()
            else:
                return None

def __getCandelsTimed(symbol: str, interval: candles.candleInterval, amount: int, startPoint: int):
    return __client.klines(symbol, interval, startTime = startPoint, limit = amount)

def __parseResponce(responceCandles, interval: candles.candleInterval):
    candle = candles.Candle()
    candle.interval = interval
    candle.openTime = responceCandles[0]
    candle.closeTime = responceCandles[6]
    candle.time = datetime.fromtimestamp(responceCandles[0] / 1000).strftime('%H:%M %d-%m-%Y')
    candle.open = float(responceCandles[1])
    candle.high = float(responceCandles[2])
    candle.low = float(responceCandles[3])
    candle.close = float(responceCandles[4])
    candle.volume = float(responceCandles[5])
    return candle

def __getCandles(symbol: str, interval: candles.candleInterval, amount: int, startPoint: int):
    result = []
    intervalStr = candles.candleIntervalToStr[interval]
    startAmount = amount
    while amount > 0:
        amountStep = min(amount, __maxCandelsAmount)
        result.extend(__getCandelsTimed(symbol, intervalStr, amountStep, startPoint))
        if startPoint == 0:
            startPoint = result[0][0]
            amount = int(utils.floor((utils.getCurrentTime() - result[0][0]) / interval, 0))
            startAmount = amount
        amount -= amountStep
        startPoint = result[-1][0] + interval
        print(int((startAmount - amount) / startAmount * 100))

    return [__parseResponce(responce, interval) for responce in result]

def getCandelsByAmount(symbol: str, interval: candles.candleInterval, amount: int):
    startPoint = utils.getCurrentTime() - amount * interval
    return __makeApiCall(__getCandles(symbol, interval, amount, startPoint))

def getFinishedCandelsByStart(symbol: str, interval: candles.candleInterval, startPoint: int, amount: int = -1):
    if amount == -1:
        amount = int(utils.floor((utils.getCurrentTime() - startPoint) / interval, 0))
    return __makeApiCall(__getCandles(symbol, interval, amount, startPoint))

def getExchangeInfo():
    return __makeApiCall(__client.exchange_info())
