from models import timeframe
from enum import Enum
from datetime import datetime

class LastCandleState(Enum):
    INVALID = 0,
    DIRTY = 1,
    VALID = 2

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

        self.volume = 0

        self.atr = None
        self.rsi = None

        self.vertexHigh = None
        self.vertexStrengthHigh = 0

        self.vertexLow = None
        self.vertexStrengthLow = 0
        
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
        and self.close == __value.close \
        and self.volume == __value.volume
    
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
    result.append(candle.volume)
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
    result.volume = data[5]
    result.closeTime = result.openTime + result.interval - 1
    return result

def toSpotJson(candle:Candle):
    result = toJson(candle)
    result.append(candle.closeTime)
    return result

def fromSpotJson(data, tf:str):
    result = fromJson(data, tf)
    result.closeTime = data[6]
    return result
