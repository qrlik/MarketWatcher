import api.third_party.ibkr as ibkr
import api.stocks as stocks
from utilities import utils

def __updateIbkrExceptions():
    ibkr.runApp()
    ibkr.app.checkTickersList(stocks.getTickersList(), False)
    while ibkr.app.isLoading():
        pass
    exceptions = ibkr.app.getUnknownTickers()
    utils.saveJsonFile('parsedException', exceptions)

if __name__ == '__main__':
    __updateIbkrExceptions()