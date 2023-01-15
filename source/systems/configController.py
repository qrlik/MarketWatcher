from models import enums
from utilities import utils

__configs:dict = {}

def save(filename:str):
	if len(filename) == 0:
		return
	utils.saveBsonFile(filename, __configs)

def load():
	pass

def addConfig(timeframe:str):
	__configs.setdefault(timeframe, {})

def deleteConfig(timeframe:str):
	__configs.pop(timeframe)

def updateConfig(timeframe:enums.Timeframe, config, value):
	timeFrameConfigs = __configs.setdefault(timeframe, {})
	configValue = timeFrameConfigs.setdefault(config, value)
	configValue = value

def clear():
	__configs.clear()