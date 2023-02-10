from models import enums

candleIntervalToStr = {
    enums.Timeframe.ONE_MIN : '1m',
    enums.Timeframe.THREE_MIN : '3m',
    enums.Timeframe.FIVE_MIN : '5m',
    enums.Timeframe.FIFTEEN_MIN : '15m',
    enums.Timeframe.THIRTY_MIN : '30m',
    enums.Timeframe.ONE_HOUR : '1h',
    enums.Timeframe.TWO_HOUR : '2h',
    enums.Timeframe.FOUR_HOUR : '4h',
    enums.Timeframe.SIX_HOUR : '6h',
    enums.Timeframe.EIGHT_HOUR : '8h',
    enums.Timeframe.TWELVE_HOUR : '12h',
    enums.Timeframe.ONE_DAY : '1d',
    enums.Timeframe.THREE_DAY : '3d',
    enums.Timeframe.ONE_WEEK : '1w',
    enums.Timeframe.ONE_MONTH : '1M' }

class Candle:
    interval = None
    openTime = 0
    closeTime = 0
    time = ''

    open = 0.0
    high = 0.0
    low = 0.0
    close = 0.0