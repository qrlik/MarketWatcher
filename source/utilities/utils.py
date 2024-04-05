import json
import msgspec
import os.path
import math
import time
import logging
import sys
from logging.handlers import RotatingFileHandler

cacheFolder = 'cache/'
assetsFolder = 'assets/'
__listeners = set()

def setupLogger(name, file, level):
    if not os.path.exists(file):
        if not os.path.exists('cache'):
            os.mkdir('cache')
        with open(file, 'x') as f:
            f.write('')

    handler = RotatingFileHandler(file, maxBytes=100*1024*1024, backupCount=2)        
    handler.setFormatter(logging.Formatter(fmt='%(asctime)s.%(msecs)06d %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

__infoLogger = setupLogger('infoLogger', cacheFolder + 'Logs.txt', logging.INFO)
__errorLogger = setupLogger('errorLogger', cacheFolder + 'errorLogs.txt', logging.ERROR)

def getCurrentTime() -> int:
    return round(time.time() * 1000)

def getCurrentTimeSeconds() -> int:
    return round(time.time())

def loadJsonFile(filename):
    try:
        with open(filename + '.json') as infile:
            return json.load(infile)
    except Exception as e:
        logError(str(e))
        return None

def saveJsonFile(filename, data):
    try:
        with open(filename + '.json', 'w') as outfile:
            json.dump(data, outfile)
    except Exception as e:
        logError(str(e))
        return None
    
# def loadJsonMsgspecFile(filename):
#     try:
#         with open(filename + '.json', 'rb') as infile:
#             return msgspec.json.decode(infile.read())
#     except Exception as e:
#         logError(str(e))
#         return None

# def saveJsonMsgspecFile(filename, data):
#     try:
#         with open(filename + '.json', 'wb') as outfile:
#             outfile.write(msgspec.json.encode(data))
#     except Exception as e:
#         logError(str(e))
#         return None
    
def addLogListener(obj):
    __listeners.add(obj)

def __logListeners(logStr):
    for listener in __listeners:
        method = getattr(listener, 'log', None)
        if callable(method):
            method(logStr)

def log(text: str, obj = None):
    source = '' if not obj else type(obj).__name__ + ': '
    logStr = source + text
    __infoLogger.info(logStr)
    __logListeners(logStr)

def logError(text: str, obj = None):
    source = '' if not obj else type(obj).__name__ + ': '
    logStr = source + text
    __errorLogger.error(logStr)
    __logListeners(logStr)
    print(logStr)

def isDebug():
    """Return if the debugger is currently active"""
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None

def ceil(value: float, degree: int = 2) -> float:
    tens = math.pow(10, degree)
    return math.ceil(value * tens) / tens

def floor(value: float, degree: int = 2) -> float:
    tens = math.pow(10, degree)
    return math.floor(value * tens) / tens

def less(lhs, rhs):
    return lhs < rhs

def greater(lhs, rhs):
    return lhs > rhs
