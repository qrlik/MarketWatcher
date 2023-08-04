
from tests import testAtr
from tests import testRsi
from tests import testVertex

from api import stocks
from api.third_party import yahoo
from models import candle
from models import timeframe

def testAll():
    testAtr.test()
    testRsi.test()
    testVertex.test()

if __name__ == '__main__':
    tickers = stocks.getTickers()
    interval = timeframe.Timeframe.ONE_DAY
    for ticker in tickers:
        data = yahoo.get_data(ticker, timeframe.tfToYahooApiStr[interval], interval, start_date = '07/01/2023', )
        candles = [candle.fromJson(c, interval.name) for c in data]
        x = 1

    #testAll()