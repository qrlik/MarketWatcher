from enum import IntEnum

class Timeframe(IntEnum):
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
    ONE_WEEK = 604_800_000

timeframeToApiStr = {
    Timeframe.ONE_MIN : '1m',
    Timeframe.THREE_MIN : '3m',
    Timeframe.FIVE_MIN : '5m',
    Timeframe.FIFTEEN_MIN : '15m',
    Timeframe.THIRTY_MIN : '30m',
    Timeframe.ONE_HOUR : '1h',
    Timeframe.TWO_HOUR : '2h',
    Timeframe.FOUR_HOUR : '4h',
    Timeframe.SIX_HOUR : '6h',
    Timeframe.EIGHT_HOUR : '8h',
    Timeframe.TWELVE_HOUR : '12h',
    Timeframe.ONE_DAY : '1d',
    Timeframe.THREE_DAY : '3d',
    Timeframe.ONE_WEEK : '1w' }

apiToTimeframe = {
    '1m' : Timeframe.ONE_MIN,
    '3m' : Timeframe.THREE_MIN,
    '5m' : Timeframe.FIVE_MIN,
    '15m' : Timeframe.FIFTEEN_MIN,
    '30m' : Timeframe.THIRTY_MIN,
    '1h' : Timeframe.ONE_HOUR,
    '2h' : Timeframe.TWO_HOUR,
    '4h' : Timeframe.FOUR_HOUR,
    '6h' : Timeframe.SIX_HOUR,
    '8h' : Timeframe.EIGHT_HOUR,
    '12h' : Timeframe.TWELVE_HOUR,
    '1d' : Timeframe.ONE_DAY,
    '3d' : Timeframe.THREE_DAY,
    '1w' : Timeframe.ONE_WEEK }

timeframeToPrettyStr = {
    Timeframe.ONE_MIN : '1m',
    Timeframe.THREE_MIN : '3m',
    Timeframe.FIVE_MIN : '5m',
    Timeframe.FIFTEEN_MIN : '15m',
    Timeframe.THIRTY_MIN : '30m',
    Timeframe.ONE_HOUR : '1h',
    Timeframe.TWO_HOUR : '2h',
    Timeframe.FOUR_HOUR : '4h',
    Timeframe.SIX_HOUR : '6h',
    Timeframe.EIGHT_HOUR : '8h',
    Timeframe.TWELVE_HOUR : '12h',
    Timeframe.ONE_DAY : 'D',
    Timeframe.THREE_DAY : '3D',
    Timeframe.ONE_WEEK : 'W' }

def getPrettyFormat(timeframe:Timeframe):
    return timeframeToPrettyStr.get(timeframe)
