from utilities import utils

__settings:dict = utils.loadJsonFile('assets/globalSettings')

def getSetting(key:str):
	return __settings.get(key)
