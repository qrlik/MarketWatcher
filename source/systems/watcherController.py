from api import api

def getTickersList():
    #tmp
    return [ 'BTCUSDT' ]
    info = api.Spot.getExchangeInfo()
    tickers = []
    for symbol in info.get('symbols', []):
        if symbol.get('status', '') == 'TRADING' and symbol.get('quoteAsset', '') == 'USDT':
            name = symbol.get('symbol')
            if name:
                tickers.append(name)
    return tickers
    