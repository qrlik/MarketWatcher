
from datetime import datetime
from threading import Lock
import certifi
import os

from api import api
from models import candle
from models import timeframe
from utilities import utils

os.environ['SSL_CERT_FILE'] = certifi.where()

__ticketsData = {}
__timeframe = None
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
                utils.logError('tickerData::__checkSequence wrong sequence')

    def update(self, time, candle:candle.Candle, isClosed):
        with self.lock:
            if isClosed:
                if not self.finishedCandle or candle.openTime > self.finishedCandle.openTime:
                    self.finishedCandle = candle
                    self.currentCandle = None
                    self.lastEventTime = 0
            else:
                if not self.currentCandle:
                    self.currentCandle = candle
                    self.lastEventTime = time
                    if self.finishedCandle and self.finishedCandle.openTime + self.finishedCandle.interval != self.currentCandle.openTime:
                        self.finishedCandle = None
                elif candle.openTime > self.currentCandle.openTime:
                    self.finishedCandle = None
                    self.currentCandle = candle
                    self.lastEventTime = time
                elif time > self.lastEventTime:
                    self.currentCandle = candle
                    self.lastEventTime = time
            self.__checkSequence()

    def get(self):
        result = None
        with self.lock:
            result = (self.currentCandle, self.finishedCandle)
        return result

def start(tickets:list, tf:timeframe.Timeframe):
    global __timeframe, __started
    if __started:
        return
    __started = True
    __timeframe = tf
    for ticket in tickets:
        __ticketsData.setdefault(ticket, tickerData())
    api.Spot.subscribeKlines(tickets, tf, onMessage)

def parseCandle(data):
    c = candle.Candle()
    c.interval = __timeframe
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
    
    c, isClosed = parseCandle(data['k'])
    __ticketsData[ticker].update(time, c, isClosed)