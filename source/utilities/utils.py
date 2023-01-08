import json
import os.path
import math
import time
import logging

__logsFile = 'logs/Logs.txt'
if not os.path.exists(__logsFile):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    with open(__logsFile, 'x') as f:
        f.write('')

logging.basicConfig(
    format='%(asctime)s.%(msecs)06d %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(__logsFile),
        #logging.StreamHandler()
    ])
    
def getCurrentTime() -> int:
    return round(time.time() * 1000)

def loadJsonFile(filename):
    try:
        with open(filename + '.json') as infile:
            return json.load(infile)
    except:
        return None

def saveJsonFile(filename, data):
    with open(filename + '.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

def log(text: str, obj = None):
    source = '' if not obj else type(obj).__name__ + ': '
    logStr = source + text
    logging.info(logStr)

def ceil(value: float, degree: int = 2) -> float:
    tens = math.pow(10, degree)
    return math.ceil(value * tens) / tens

def floor(value: float, degree: int = 2) -> float:
    tens = math.pow(10, degree)
    return math.floor(value * tens) / tens
