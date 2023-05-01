import json
import jsonpickle
import os.path
import math
import time
import logging
import sys
from logging.handlers import RotatingFileHandler

cacheFolder = 'cache/'
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

    if level == logging.ERROR:
        stream = logging.StreamHandler()        
        stream.setFormatter(logging.Formatter(fmt='%(asctime)s.%(msecs)06d %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(stream)

    return logger

__infoLogger = setupLogger('infoLogger', cacheFolder + 'Logs.txt', logging.INFO)
__errorLogger = setupLogger('errorLogger', cacheFolder + 'errorLogs.txt', logging.ERROR)

def getCurrentTime() -> int:
    return round(time.time() * 1000)

def loadJsonFile(filename):
    try:
        with open(filename + '.json') as infile:
            return json.load(infile)
    except Exception as e:
        return None

def loadPickleJson(filename):
    try:
        with open(filename + '.json') as infile:
            return jsonpickle.decode(infile.read())
    except Exception as e:
        return None

def saveJsonFile(filename, data):
    try:
        with open(filename + '.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
    except:
        return None
    
def savePickleJson(filename, data):
    with open(filename + '.json', 'w') as outfile:
        outfile.write(jsonpickle.encode(data))

def addLogListener(obj):
    __listeners.add(obj)

def deleteLogListener(obj):
    __listeners.remove(obj)

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

def isDebug():
    """Return if the debugger is currently active"""
    return hasattr(sys, 'gettrace') and sys.gettrace() is not None

def ceil(value: float, degree: int = 2) -> float:
    tens = math.pow(10, degree)
    return math.ceil(value * tens) / tens

def floor(value: float, degree: int = 2) -> float:
    tens = math.pow(10, degree)
    return math.floor(value * tens) / tens
