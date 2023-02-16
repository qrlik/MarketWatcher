import json
import os.path
import math
import time
import logging
from logging.handlers import RotatingFileHandler

__logsFile = 'tmp/Logs.txt'
if not os.path.exists(__logsFile):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    with open(__logsFile, 'x') as f:
        f.write('')

logging.basicConfig(
    format='%(asctime)s.%(msecs)06d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        RotatingFileHandler(__logsFile, maxBytes=100*1024*1024, backupCount=2)
    ])

def getCurrentTime() -> int:
    return round(time.time() * 1000)

def loadJsonFile(filename, isBson = False):
    try:
        with open(filename + ('.bson' if isBson else '.json')) as infile:
            return json.load(infile)
    except:
        return None

def saveJsonFile(filename, data, isBson = False):
    with open(filename + ('.bson' if isBson else '.json'), 'w') as outfile:
        json.dump(data, outfile, indent=4)

def log(text: str, obj = None):
    source = '' if not obj else type(obj).__name__ + ': '
    logStr = source + text
    logging.info(logStr)

def logError(text: str, obj = None):
    source = '' if not obj else type(obj).__name__ + ': '
    logStr = source + text
    logging.error(logStr)

def ceil(value: float, degree: int = 2) -> float:
    tens = math.pow(10, degree)
    return math.ceil(value * tens) / tens

def floor(value: float, degree: int = 2) -> float:
    tens = math.pow(10, degree)
    return math.floor(value * tens) / tens
