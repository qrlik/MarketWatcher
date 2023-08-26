import api.third_party.yahoo as yahoo
import api.apiRequests as apiRequests
from utilities import utils

def init():
    pass

def __exceptTickers(tickers):
    exceptions = set()
    correct = set()
    data = utils.loadJsonFile(utils.assetsFolder + 'stockData')

    for _, list in data.get('exceptions', {}).items():
        exceptions.update(list)
    for ticker, _ in data.get('data', {}).items():
        correct.add(ticker)

    correctAndNew = tickers.difference(exceptions)
    new = correctAndNew.difference(correct)

    if len(new) > 0:
        utils.log('Have new ' + str(len(new)) + ' tickers, run script')

    return correctAndNew.difference(new)

def getTickersList(withExcept=True):
    tickers = set()
    sp500 = yahoo.tickers_sp500()
    dow = yahoo.tickers_dow()
    nasdaq = yahoo.tickers_nasdaq()
    #other = si.tickers_other()

    tickers.update(sp500)
    tickers.update(dow)
    tickers.update(nasdaq)
    #tickers.update(other)

    if withExcept:
        tickers = __exceptTickers(tickers)

    return sorted(list(tickers))

def getStockCandels(symbol: str, interval: str, startTime: int):
    return apiRequests.requester.addAsyncRequest(yahoo.get_data, symbol, interval, startTime)
