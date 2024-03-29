from PySide6.QtCore import Qt
from datetime import datetime
import time

from api import api
from utilities import guiDefines
from utilities import utils
from utilities import workMode

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
            return guiDefines.bullColor
        elif isShort:
            return guiDefines.bearColor
        else:
            return guiDefines.defaultFontColor

def __requestPositions():
    global __data
    poses = api.getPositions()
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

def init():
    if workMode.isStock():
        return
    global __keyTime
    __requestPositions()
    api.subscribePositions(__userDataStream)
    __keyTime = int(time.time())

def update():
    if workMode.isStock():
        return
    global __keyTime
    curTime = int(time.time())
    if curTime - __keyTime >= 3000: #update key every 50 min
        api.getListenKey()
        __keyTime = int(time.time())

def getTickerUserData(ticker:str):
    return __data.get(ticker, TickerData())

def getTickerJsonData(ticker:str):
    data = getTickerUserData(ticker)
    result = {}

    positionData = None
    type = ''
    if data.longPosition.isOpened():
        positionData = data.longPosition
        type = 'LONG'
    if data.shortPosition.isOpened():
        if not positionData or data.shortPosition.lastUpdate > data.longPosition.lastUpdate:
            positionData = data.shortPosition
            type = 'SHORT'

    if positionData is None:
        positionData = PositionInfo()
    result.setdefault('time', datetime.fromtimestamp(positionData.lastUpdate / 1000).strftime('%H:%M %d-%m-%Y'))
    result.setdefault('type', type)
    result.setdefault('price', positionData.averagePrice)

    return result
