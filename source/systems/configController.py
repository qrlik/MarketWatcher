from models import timeframe
from utilities import utils
from utilities import workMode

__configs:dict = {}

def save(filename:str):
	if len(filename) == 0:
		return
	utils.saveJsonFile(filename, __configs)

def load():
	#(cacheController.getLastConfigFilename())
	filename = workMode.getConfigFile()
	if not filename or len(filename) == 0:
		return
	global __configs
	loaded = utils.loadJsonFile(filename)
	if loaded is not None and len(loaded) > 0:
		__configs = loaded

def clear():
	__configs.clear()

def getGlobalConfigs():
	return __configs.get('globalConfigs', {}).items()

def getGlobalConfig(name:str):
	return __configs.get('globalConfigs', {}).get(name)

def setGlobalConfig(name:str, value):
	globals = __configs.setdefault('globalConfigs', {})
	globals.setdefault(name, None)
	globals[name] = value

def addTimeframe(timeframe:str):
	__configs.setdefault('timeframes', {}).setdefault(timeframe, {})

def deleteTimeframe(timeframe:str):
	__configs.setdefault('timeframes', {}).pop(timeframe, None)

def getTimeframes():
	result = [timeframe.Timeframe[tf] for tf in __configs.get('timeframes', {}).keys()]
	return sorted(result)

# def getTimeframesConfigs():
# 	return __configs.get('timeframes', {}).items()

def getConfigState(timeframe:str, config:str):
	configs = __configs.get('timeframes', {}).get(timeframe, {})
	return configs.get(config, None)

# def __setConfigState(timeframe:str, config:str, name:str, value):
# 	config = __configs.setdefault('timeframes', {}).setdefault(timeframe, {}).setdefault(config, {})
# 	config.setdefault(name, False)
# 	config[name] = value
