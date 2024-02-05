import api.third_party.ibkr as ibkr
import api.stocks as stocks
from utilities import utils

# Get tickers list from yahoo
# Filter by stockType,industry,category from ibkrExceptions.json
# Get Final Data (ruleIds, data, exceptions, backets)
# 
# When request with info, dismiss expceptions, then dismiss new tickers (without ibkr info)

def __updateIbkrExceptions():
    ibkr.runApp()
    ibkr.app.checkTickersList(stocks.getTickersList(False))
    while ibkr.app.isLoading():
        pass
    exceptions = ibkr.app.getFinalData()
    utils.saveJsonFile('stockData', exceptions)
    ibkr.app.disconnect()

if __name__ == '__main__':
    __updateIbkrExceptions()