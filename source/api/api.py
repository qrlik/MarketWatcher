
from enum import IntEnum

from api import stocks
from api import crypto
from api.third_party import yahoo
from models import timeframe
from utilities import workMode

import time

class CryptoMode(IntEnum):
    SPOT = 0,
    FUTURE = 1

def init():
    if workMode.isCrypto():
        crypto.init()
    else:
        stocks.init()

def isExpectNewCandles(openTime, interval:timeframe.Timeframe):
    if workMode.isStock():
        return yahoo.isExpectNewCandles(openTime / 1000, timeframe.tfToYahooApiStr[interval])

def getTickersList():
    if workMode.isCrypto():
        return crypto.getTickersList()
    else:
        result = []
        for ticket in stocks.getTickersList():
            data = []
            data.append(ticket)
            data.append('')
            data.append(2)
            result.append(data)
        return result

def getPositions():
    if workMode.isCrypto():
        return crypto.Future.getPositions()
    return []

def getListenKey():
    if workMode.isCrypto():
        return crypto.Future.getListenKey()

def subscribePositions(callback):
    if workMode.isCrypto():
        return crypto.Future.subscribePositions(callback)

def subscribeKlines(tickets, interval: timeframe.Timeframe, callback):
    if workMode.isCrypto():
        return crypto.Spot.subscribeKlines(tickets, interval, callback)

def getCandlesByTimestamp(symbol: str, interval: timeframe.Timeframe, amount: int, startPoint: int):
    if workMode.isCrypto():
        return crypto.Spot.getCandlesByTimestamp(symbol, interval, amount, startPoint)

def getCandels(symbol: str, interval: timeframe.Timeframe, amount: int):
    if workMode.isCrypto():
        return crypto.Spot.getCandels(symbol, interval, amount)
    
def getStockCandels(symbol: str, interval: timeframe.Timeframe, startTime: int):
    if workMode.isStock():
        return stocks.getStockCandels(symbol, timeframe.tfToYahooApiStr[interval], startTime / 1000)
    
def getExpectedStartPoint(interval: timeframe.Timeframe, amount:int):
    if interval not in [timeframe.Timeframe.ONE_DAY, timeframe.Timeframe.ONE_WEEK, timeframe.Timeframe.ONE_MONTH]:
        raise AssertionError('error tf')
    curTime = int(time.time() * 1000)
    return curTime - 2 * amount * interval

def atExit():
    if workMode.isCrypto():
        crypto.atExit()