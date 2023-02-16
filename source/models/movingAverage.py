from enum import Enum

class MovingAverageType(Enum):
	MA20 = 1,
	MA50 = 2,
	MA100 = 3,
	MA200 = 4,
        
	EMA21 = 5,
	EMA55 = 6,
	EMA100 = 7,
	EMA144 = 8,
	EMA200 = 9

class MovingAverageMode(Enum):
    SMA = 0,
    EMA = 1

MovingAverageData = {
    MovingAverageType.MA20: (20, MovingAverageMode.SMA),
    MovingAverageType.MA50: (50, MovingAverageMode.SMA),
    MovingAverageType.MA100: (100, MovingAverageMode.SMA),
    MovingAverageType.MA200: (200, MovingAverageMode.SMA),

    MovingAverageType.EMA21: (21, MovingAverageMode.EMA),
    MovingAverageType.EMA55: (55, MovingAverageMode.EMA),
    MovingAverageType.EMA100: (100, MovingAverageMode.EMA),
    MovingAverageType.EMA144: (144, MovingAverageMode.EMA),
    MovingAverageType.EMA200: (200, MovingAverageMode.EMA)
}

def getMaxAverageSize(container):
    maxSize = 0
    for average in container:
        if isinstance(average, MovingAverageType):
            maxSize = max(maxSize, MovingAverageData[average][0])
    return maxSize

