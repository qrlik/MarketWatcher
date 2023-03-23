from utilities import utils

__settings:dict = utils.loadJsonFile('assets/globalConfigs', True)

def getConfig(key:str):
	return __settings.get(key)
