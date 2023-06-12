from PySide6.QtCore import Qt
import time

from api import api
from utilities import utils

__data:dict = {}
__keyTime = 0

class PositionInfo:
    def __init__(self):
        self.amount = 0.0
        self.averagePrice = 0.0
        self.lastUpdate = 0

    def isOpened(self):
        return abs(self.amount) > 0.0

    def parseFromResponse(self, data):
        self.amount = float(data.get('positionAmt', 0.0))
        self.averagePrice = float(data.get('entryPrice', 0.0))
        self.lastUpdate = int(data.get('updateTime', 0))

    def parseFromStream(self, time, data):
        if time < self.lastUpdate:
            utils.logError('PositionInfo not actual stream event')
            return
        self.amount = float(data.get('pa', 0.0))
        self.averagePrice = float(data.get('ep', 0.0))
        self.lastUpdate = time
    
class TickerData:
    def __init__(self):
        self.longPosition = PositionInfo()
        self.shortPosition = PositionInfo()

    def parsePositionResponse(self, data):
        side = data.get('positionSide', '')
        if side == 'LONG':
            self.longPosition.parseFromResponse(data)
        elif side == 'SHORT':
            self.shortPosition.parseFromResponse(data)

    def parsePositionStream(self, time, data):
        side = data.get('ps', '')
        if side == 'LONG':
            self.longPosition.parseFromStream(time, data)
        elif side == 'SHORT':
            self.shortPosition.parseFromStream(time, data)

    def isOpened(self):
        return self.longPosition.isOpened() or self.shortPosition.isOpened()
    
    def getLastUpdate(self):
        isLong = self.longPosition.isOpened()
        isShort = self.shortPosition.isOpened()
        if isLong and isShort:
            return max(self.longPosition.lastUpdate, self.shortPosition.lastUpdate)
        elif isLong:
            return self.longPosition.lastUpdate
        elif isShort:
            return self.shortPosition.lastUpdate
        else:
            return 0

    def getPositionColor(self):
        isLong = self.longPosition.isOpened()
        isShort = self.shortPosition.isOpened()
        if isLong and isShort:
            return Qt.GlobalColor.darkYellow
        elif isLong:
            return Qt.GlobalColor.darkGreen
        elif isShort:
            return Qt.GlobalColor.darkRed
        else:
            return Qt.GlobalColor.black

def __requestPositions():
    global __data
    poses = api.Future.getPositions()
    for pose in poses:
        symbol = pose.get('symbol', None)
        if symbol is not None:
            info = __data.setdefault(symbol, TickerData())
            info.parsePositionResponse(pose)

def __userDataStream(data):
    global __data
    event = data.get('e', '')
    time = data.get('E', 0)
    if event == 'ACCOUNT_UPDATE':
        new = data.get('a', {})
        for pos in new.get('P', {}):
            symbol = pos.get('s', None)
            if symbol is not None:
                info = __data.setdefault(symbol, TickerData())
                info.parsePositionStream(time, pos)

def getTickerUserData(ticker:str):
    return __data.get(ticker, TickerData())

def init():
    global __keyTime
    __requestPositions()
    api.Future.subscribePositions(__userDataStream)
    __keyTime = int(time.time())

def update():
    global __keyTime
    curTime = int(time.time())
    if curTime - __keyTime >= 3000: #update key every 50 min
        api.Future.getListenKey()
        __keyTime = int(time.time())


