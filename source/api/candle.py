from enum import IntEnum

class candleInterval(IntEnum):
    ONE_MIN = 60_000,
    THREE_MIN = 180_000,
    FIVE_MIN = 300_000,
    FIFTEEN_MIN = 900_000,
    THIRTY_MIN = 1_800_000,
    ONE_HOUR = 3_600_000,
    TWO_HOUR = 7_200_000,
    FOUR_HOUR = 14_400_000,
    SIX_HOUR = 21_600_000,
    EIGHT_HOUR = 28_800_000,
    TWELVE_HOUR = 43_200_000,
    ONE_DAY = 86_400_000,
    THREE_DAY = 259_200_000,
    ONE_WEEK = 604_800_000,
    ONE_MONTH = -1

candleIntervalToStr = {
    candleInterval.ONE_MIN : '1m',
    candleInterval.THREE_MIN : '3m',
    candleInterval.FIVE_MIN : '5m',
    candleInterval.FIFTEEN_MIN : '15m',
    candleInterval.THIRTY_MIN : '30m',
    candleInterval.ONE_HOUR : '1h',
    candleInterval.TWO_HOUR : '2h',
    candleInterval.FOUR_HOUR : '4h',
    candleInterval.SIX_HOUR : '6h',
    candleInterval.EIGHT_HOUR : '8h',
    candleInterval.TWELVE_HOUR : '12h',
    candleInterval.ONE_DAY : '1d',
    candleInterval.THREE_DAY : '3d',
    candleInterval.ONE_WEEK : '1w',
    candleInterval.ONE_MONTH : '1M' }

class Candle:
    interval = None
    openTime = 0
    closeTime = 0
    time = ''

    open = 0.0
    high = 0.0
    low = 0.0
    close = 0.0