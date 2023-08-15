import api.third_party.yahoo as yahoo
import api.apiRequests as apiRequests

def init():
    pass

def getTickersList():
    tickers = set()
    sp500 = yahoo.tickers_sp500()
    dow = yahoo.tickers_dow()
    #nasdaq = si.tickers_nasdaq()
    #other = si.tickers_other()

    tickers.update(sp500)
    tickers.update(dow)
    #tickers.update(nasdaq)
    #tickers.update(other)
    result = []

    # tmp exception list
    tickers.discard('BRK.B')
    tickers.discard('BF.B')

    sortedTickets = sorted(list(tickers))
    for ticket in sortedTickets:
        data = []
        data.append(ticket)
        data.append('')
        data.append(2)
        result.append(data)
    return result

def getStockCandels(symbol: str, interval: str, startTime: int):
    return apiRequests.requester.addAsyncRequest(yahoo.get_data, symbol, interval, startTime)