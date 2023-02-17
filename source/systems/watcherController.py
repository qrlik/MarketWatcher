from api import api
from systems import tickerController

def getTickersList():
    info = api.Spot.getExchangeInfo()
    tickers = []
    for symbol in info.get('symbols', []):
        if symbol.get('status', '') == 'TRADING' and symbol.get('quoteAsset', '') == 'USDT':
            name = symbol.get('symbol')
            if name:
                tickers.append(name)
    return tickers
    
def tmp():
    x = tickerController.TickerController('BTCUSDT')

#     averages = [ movingAverage.MovingAverageType.EMA21 ]
#     controller = movingAverageController.MovingAverageController(averages)

#     candles = api.Spot.getCandelsByAmount('BTCUSDT', timeframe.Timeframe.ONE_HOUR, 147)
#     candles.pop()
#     for candle in candles:
#         controller.process(candle)

#     averages = controller.getAverages()
 