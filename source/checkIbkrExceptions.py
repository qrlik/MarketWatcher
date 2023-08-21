import api.third_party.ibkr as ibkr
import api.stocks as stocks
from utilities import utils

def __updateIbkrExceptions():
    ibkr.runApp()
    ibkr.app.checkTickersList(stocks.getTickersList(False)) # to do change to list/set
    while ibkr.app.isLoading():
        pass
    exceptions = ibkr.app.getInvalidTickers()
    utils.saveJsonFile('parsedException', exceptions)
    ibkr.app.disconnect()

if __name__ == '__main__':
    __updateIbkrExceptions()