
from datetime import datetime
from threading import Lock
import certifi
import os

from api import api
from models import candle
from models import timeframe
from utilities import utils

os.environ['SSL_CERT_FILE'] = certifi.where()

__tickersData = {}
__started = False

class tickerData:
    def __init__(self):
        self.finishedCandle = None
        self.currentCandle = None
        self.lastEventTime = 0
        self.lock = Lock()

    def __checkSequence(self):
        if self.finishedCandle and self.currentCandle:
            if self.finishedCandle.openTime + self.finishedCandle.interval != self.currentCandle.openTime:
                utils.logError('websocketController::__checkSequence wrong sequence')

    def __setFinished(self, finished):
        self.finishedCandle = finished
        self.currentCandle = None
        self.lastEventTime = 0

    def update(self, time, candle:candle.Candle, isClosed):
        with self.lock:
            if isClosed:
                if self.currentCandle:
                    if self.currentCandle.openTime == candle.openTime \
                    or self.currentCandle.openTime < candle.openTime:
                        self.__setFinished(candle)
                elif self.finishedCandle:
                    if self.finishedCandle.openTime < candle.openTime:
                        self.__setFinished(candle)
                else:
                        self.__setFinished(candle)
            else:
                if self.currentCandle:
                    if self.currentCandle.openTime == candle.openTime and time > self.lastEventTime:
                        self.currentCandle = candle
                        self.lastEventTime = time
                    elif self.currentCandle.openTime < candle.openTime:
                        self.finishedCandle = None
                        self.currentCandle = candle
                        self.lastEventTime = time
                elif self.finishedCandle:
                    self.currentCandle = candle
                    self.lastEventTime = time
                    if self.finishedCandle.openTime + self.finishedCandle.interval != self.currentCandle.openTime:
                        self.finishedCandle = None
                else:
                    self.currentCandle = candle
                    self.lastEventTime = time
            self.__checkSequence()

    def get(self):
        result = None
        with self.lock:
            result = (self.currentCandle, self.finishedCandle)
        return result

def getTickerData(ticker:str, tf:timeframe.Timeframe):
    global __tickersData
    return __tickersData.get(ticker).get(tf).get()

def start(tickers:list, tfs:list):
    global __started, __tickersData
    if __started:
        return
    __started = True
    for ticker in tickers:
        for tf in tfs:
            __tickersData.setdefault(ticker, {}).setdefault(tf, tickerData())
    for tf in tfs:
        api.Spot.subscribeKlines(tickers, tf, onMessage)

def parseCandle(data):
    c = candle.Candle()
    c.interval = timeframe.apiToTimeframe.get(data['i'])
    c.openTime = data['t']
    c.closeTime = data['T']
    c.time = datetime.fromtimestamp(c.openTime / 1000).strftime('%H:%M %d-%m-%Y')
    c.open = float(data['o'])
    c.high = float(data['h'])
    c.low = float(data['l'])
    c.close = float(data['c'])
    #c.volume = float(data['v'])
    return (c, data['x'])

def onMessage(message):
    if not isinstance(message, dict):
        return
    data = message.get('data', None)
    if not data:
        return
    ticker = data.get('s', None)
    time = data.get('E', None)
    candleData = data.get('k', None)
    if not time or not candleData or not ticker:
        return
    
    global __tickersData
    c, isClosed = parseCandle(data['k'])
    __tickersData[ticker][c.interval].update(time, c, isClosed)
    #print(ticker + '\t\t' + c.time + '\t\t' + str(time) + '\t\t' + str(c.open) + '\t\t' + str(c.close) + '\t\t' + str(c.high) + '\t\t' + str(c.low) + '\t\t' + str(isClosed))