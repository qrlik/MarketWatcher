from models import timeframe

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

    def __eq__(self, __value):
        return self.interval == __value.interval \
        and self.openTime == __value.openTime \
        and self.closeTime == __value.closeTime \
        and self.time == __value.time \
        and self.open == __value.open \
        and self.high == __value.high \
        and self.low == __value.low \
        and self.close == __value.close

def toDict(candle:Candle):
    result = {}
    result.setdefault('i', candle.interval.name)
    result.setdefault('t', candle.openTime)
    result.setdefault('T', candle.closeTime)
    result.setdefault('s', candle.time)
    result.setdefault('o', candle.open)
    result.setdefault('h', candle.high)
    result.setdefault('l', candle.low)
    result.setdefault('c', candle.close)
    return result

def createFromDict(candleDict:dict):
    result = Candle()
    result.interval = timeframe.Timeframe[candleDict.get('i', None)]
    result.openTime = candleDict.get('t', 0)
    result.closeTime = candleDict.get('T', 0)
    result.time = candleDict.get('s', '')
    result.open = candleDict.get('o', 0.0)
    result.high = candleDict.get('h', 0.0)
    result.low = candleDict.get('l', 0.0)
    result.close = candleDict.get('c', 0.0)
    return result