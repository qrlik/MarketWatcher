from models import enums
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

def addConfig(timeframe:str):
	__configs.setdefault(timeframe, {})

def deleteConfig(timeframe:str):
	__configs.pop(timeframe)

def updateConfig(timeframe:enums.Timeframe, config, value):
	timeFrameConfigs = __configs.setdefault(timeframe, {})
	configValue = timeFrameConfigs.setdefault(config, value)
	configValue = value
