import api.third_party.yahoo as yahoo

def getTickers():
    tickers = set()
    sp500 = yahoo.tickers_sp500()
    dow = yahoo.tickers_dow()
    #nasdaq = si.tickers_nasdaq()
    #other = si.tickers_other()

    tickers.update(sp500)
    tickers.update(dow)
    #tickers.update(nasdaq)
    #tickers.update(other)
    return sorted(list(tickers))
