import api.third_party.yahoo as yahoo

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
    sortedTickets = sorted(list(tickers))
    for ticket in sortedTickets:
        result.append(ticket)
        result.append('')
        result.append(2)
    return result

def getStockCandels(symbol: str, interval: str, startTime: int):
    return yahoo.get_data(symbol, interval, startTime)