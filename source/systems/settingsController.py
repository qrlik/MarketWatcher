from utilities import utils

__settings:dict = utils.loadJsonFile(utils.assetsFolder + 'globalSettings')

def getSetting(key:str):
	return __settings.get(key)

def getTickerStartTimestamp(ticker:str):
	tickers = __settings.get('tickersStartTimestamps')
	return tickers.get(ticker, None)
