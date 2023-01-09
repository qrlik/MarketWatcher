import enums

candleIntervalToStr = {
    enums.candleInterval.ONE_MIN : '1m',
    enums.candleInterval.THREE_MIN : '3m',
    enums.candleInterval.FIVE_MIN : '5m',
    enums.candleInterval.FIFTEEN_MIN : '15m',
    enums.candleInterval.THIRTY_MIN : '30m',
    enums.candleInterval.ONE_HOUR : '1h',
    enums.candleInterval.TWO_HOUR : '2h',
    enums.candleInterval.FOUR_HOUR : '4h',
    enums.candleInterval.SIX_HOUR : '6h',
    enums.candleInterval.EIGHT_HOUR : '8h',
    enums.candleInterval.TWELVE_HOUR : '12h',
    enums.candleInterval.ONE_DAY : '1d',
    enums.candleInterval.THREE_DAY : '3d',
    enums.candleInterval.ONE_WEEK : '1w',
    enums.candleInterval.ONE_MONTH : '1M' }

class Candle:
    interval = None
    openTime = 0
    closeTime = 0
    time = ''

    open = 0.0
    high = 0.0
    low = 0.0
    close = 0.0