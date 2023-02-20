from models import timeframe
from models import movingAverage
from utilities import utils

__configs:dict = {}

def save(filename:str):
	if len(filename) == 0:
		return
	utils.saveJsonFile(filename, __configs, True)

def load(filename:str):
	if len(filename) == 0:
		return
	global __configs
	__configs = utils.loadJsonFile(filename, True)

def clear():
	__configs.clear()

def getConfigs():
	return __configs.keys()

def getConfig(timeframe:str):
	return __configs.get(timeframe, {})

def getMovingAverages(timeframe:str):
	averages = []
	for average, state in getConfig(timeframe).items():
		if state:
			averages.append(movingAverage.MovingAverageType[average])
	return averages

def getState(timeframe:str, config:str):
	configs = __configs.get(timeframe, {})
	return configs.get(config, False)

def addConfig(timeframe:str):
	__configs.setdefault(timeframe, {})

def deleteConfig(timeframe:str):
	__configs.pop(timeframe)

def isEmpty():
	for _, configs in __configs.items():
		for configs, value in configs.items():
			if value:
				return False
	return True

def updateConfig(timeframe:timeframe.Timeframe, config, value):
	timeFrameConfigs = __configs.setdefault(timeframe, {})
	timeFrameConfigs.setdefault(config)
	timeFrameConfigs[config] = value
