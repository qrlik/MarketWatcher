from models import enums

__configs:dict = {}

def save():
	pass

def load():
	pass

def addConfig(timeframe:enums.Timeframe):
	__configs.setdefault(timeframe, {})

def deleteConfig(timeframe:enums.Timeframe):
	__configs.pop(timeframe)

def updateConfig(timeframe:enums.Timeframe, config, value):
	timeFrameConfigs = __configs.setdefault(timeframe, {})
	configValue = timeFrameConfigs.setdefault(config, value)
	configValue = value

def clear():
	__configs.clear()