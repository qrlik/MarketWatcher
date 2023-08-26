import api.third_party.ibkr as ibkr
import api.stocks as stocks
from utilities import utils

def __updateIbkrExceptions():
    ibkr.runApp()
    ibkr.app.checkTickersList(stocks.getTickersList(False))
    while ibkr.app.isLoading():
        pass
    exceptions = ibkr.app.getFinalData()
    utils.saveJsonFile('stockData', exceptions)
    ibkr.app.disconnect()

if __name__ == '__main__':
    __updateIbkrExceptions()