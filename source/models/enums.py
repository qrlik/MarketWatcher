from enum import Enum
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
    ONE_WEEK = 604_800_000,
    ONE_MONTH = -1

class MovingAverageType(Enum):
	MA_20 = 1,
	MA_50 = 2,
	MA_100 = 3,
	MA_200 = 4,
	EMA_21 = 5,
	EMA_55 = 6,
	EMA_100 = 7,
	EMA_144 = 8,
	EMA_200 = 9
