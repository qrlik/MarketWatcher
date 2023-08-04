from enum import IntEnum
from utilities import utils

class WorkMode(IntEnum):
    CRYPTO = 0,
    STOCK = 1

__type:WorkMode = WorkMode.CRYPTO

def setupWorkMode(mode:str):
    global __type
    if isinstance(mode, str):
        mode = mode.upper()
        try:
            __type = setupWorkMode[mode]
        except:
            pass

def isCrypto():
    return __type == WorkMode.CRYPTO

def isStock():
    return __type == WorkMode.STOCK

def getCacheFile():
    return utils.cacheFolder + __type.name.lower() + 'Cache'

def getCacheCandlesFile():
    return utils.cacheFolder + __type.name.lower() + 'Candles'

def getConfigFile():
    return utils.assetsFolder + __type.name.lower() + 'Config'

