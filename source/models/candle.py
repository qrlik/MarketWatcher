from models import timeframe

from datetime import datetime

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

        self.atr = None
        self.rsi = None
        self.vertex = None
        self.vertexStrength = 0

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
    result.closeTime = result.openTime + result.interval - 1
    result.time = datetime.fromtimestamp(result.openTime / 1000).strftime('%H:%M %d-%m-%Y')
    result.open = data[1]
    result.high = data[2]
    result.low = data[3]
    result.close = data[4]
    return result
