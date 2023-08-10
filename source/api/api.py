
from enum import IntEnum

from api import stocks
from api import crypto
from models import timeframe
from utilities import workMode

class CryptoMode(IntEnum):
    SPOT = 0,
    FUTURE = 1

def init():
    if workMode.isCrypto():
        crypto.init()
    else:
        stocks.init()

def getExchangeInfo(mode:CryptoMode = None):
    if workMode.isCrypto():
        assert(mode is not None)
        if mode == CryptoMode.SPOT:
            return crypto.Spot.getExchangeInfo()
        else:
            return crypto.Future.getExchangeInfo()
    else:
        pass

def getPositions():
    if workMode.isCrypto():
        return crypto.Future.getPositions()

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