
from tests import testAtr
from tests import testRsi
from tests import testVertex

from api import stocks
from api.third_party import yahoo
from models import candle
from models import timeframe
from utilities import utils

import datetime

def testAll():
    testAtr.test()
    testRsi.test()
    testVertex.test()

if __name__ == '__main__':
    testAll()
    
    # tickers = stocks.getTickersList()
    # interval = timeframe.Timeframe.ONE_MONTH
    # for ticker, info in tickers:
    #     data = yahoo.get_data(ticker[0], timeframe.tfToYahooApiStr[interval], start_date = '07/01/2022', )
    #     x = 1
    #https://query1.finance.yahoo.com/v8/finance/chart/A
    #https://query1.finance.yahoo.com/v8/finance/chart/A?interval=1mo&period1=1656633600&period2=1692598401