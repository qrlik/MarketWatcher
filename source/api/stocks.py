import api.third_party.yahoo as yahoo
import api.apiRequests as apiRequests
from utilities import utils

def init():
    pass

def getPricePrecision(price):
    return yahoo.getPricePrecision(price)

def __updateTickersInfo(tickers):
    exceptions = set()
    correct = set()
    infos = dict()
    data = utils.loadJsonFile(utils.assetsFolder + 'stockData')
    customExceptions = utils.loadJsonFile(utils.assetsFolder + 'customStockExceptions')

    for _, arr in data.get('exceptions', {}).items():
        exceptions.update(arr)
    for _, arr in customExceptions.items():
        exceptions.update(arr)

    for ticker, info in data.get('data', {}).items():
        correct.add(ticker)
        tickerInfo = {}
        tickerInfo.setdefault('name', info[0])
        tickerInfo.setdefault('industry', info[2])
        tickerInfo.setdefault('category', info[3])
        infos.setdefault(ticker, tickerInfo)

    correctAndNew = tickers.difference(exceptions)
    new = correctAndNew.difference(correct)
    if len(new) > 0:
        utils.log('Have new ' + str(len(new)) + ' tickers, run script')
        
    result = sorted(list(correctAndNew.difference(new)))
    resultWithInfo = []
    for ticker in result:
        resultWithInfo.append((ticker, infos[ticker]))
    return resultWithInfo

def getTickersList(withInfo=True):
    tickers = set()
    sp500 = yahoo.tickers_sp500()
    dow = yahoo.tickers_dow()
    nasdaq = yahoo.tickers_nasdaq(yahoo.NasdaqTier.GLOBAL_SELECT)
    #other = si.tickers_other()

    tickers.update(sp500)
    tickers.update(dow)
    tickers.update(nasdaq)
    #tickers.update(other)

    if withInfo:
        return __updateTickersInfo(tickers)

    return sorted(list(tickers))

def getStockCandels(symbol: str, interval: str, startTime: int):
    return apiRequests.requester.addAsyncRequest(yahoo.get_data, symbol, interval, startTime)
