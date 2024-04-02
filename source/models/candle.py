from models import timeframe

from datetime import datetime
import math

class Candle:
    def __init__(self):
        self.interval = None
        self.openTime = 0
        self.closeTime = 0
        self.time = ''

        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0

        self.openLog = 0.0
        self.highLog = 0.0
        self.lowLog = 0.0
        self.closeLog = 0.0

        self.atr = None
        self.rsi = None

        self.vertexHigh = None
        self.vertexLow = None

        self.vertexClose = None
        self.vertexStrengthClose = 0

        self.lastUpMaValue = None
        self.lastDownMaValue = None

    def __eq__(self, __value):
        return self.interval == __value.interval \
        and self.openTime == __value.openTime \
        and self.closeTime == __value.closeTime \
        and self.time == __value.time \
        and self.open == __value.open \
        and self.high == __value.high \
        and self.low == __value.low \
        and self.close == __value.close
    
    def __updateLogs(self):
        self.openLog = math.log(self.open)
        self.highLog = math.log(self.high)
        self.lowLog = math.log(self.low)
        self.closeLog = math.log(self.close)

def getPrettyTime(timestamp, interval):
    dt = datetime.fromtimestamp(timestamp / 1000)
    if interval == timeframe.Timeframe.ONE_MONTH \
        or interval == timeframe.Timeframe.ONE_WEEK \
        or interval == timeframe.Timeframe.ONE_DAY:
        return dt.strftime('%d %B %y')
    else:
        return dt.strftime('%H:%M %d %b')

def toJson(candle:Candle):
    result = []
    result.append(candle.openTime)
    result.append(candle.open)
    result.append(candle.high)
    result.append(candle.low)
    result.append(candle.close)
    return result

def fromJson(data, tf:str):
    result = Candle()
    result.interval = timeframe.Timeframe[tf]
    result.openTime = data[0]
    result.time = getPrettyTime(result.openTime, result.interval)
    result.open = data[1]
    result.high = data[2]
    result.low = data[3]
    result.close = data[4]
    result.closeTime = result.openTime + result.interval - 1
    result.__updateLogs()
    return result

def toSpotJson(candle:Candle):
    result = toJson(candle)
    result.append(candle.closeTime)
    return result

def fromSpotJson(data, tf:str):
    result = fromJson(data, tf)
    result.closeTime = data[5]
    return result
