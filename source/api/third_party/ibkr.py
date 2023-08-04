from ibapi.client import *
from ibapi.wrapper import *
from threading import Thread

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.__tickers = {}

        self.__requests = {}
        self.__tickersProgress = 0
        self.__tickersValidation = 0

    def getHistoricalData(self):
        possibleTickers = getTickers()
        id = 0
        for ticker in possibleTickers:
            contract = Contract()
            contract.symbol = ticker
            contract.secType = "STK"
            contract.currency = "USD"
            contract.exchange = "SMART"
            self.reqHistoricalData(id, contract, '', '1 Y', '1 day', 'TRADES', 1, 2, False, [])
            self.__requests.setdefault(id, ticker)
            id += 1
        self.__tickersProgress = id
        
    def historicalData(self, reqId:int, bar: BarData):
        super().histogramData(reqId, bar)
        self.__tickers.setdefault(self.__requests[reqId], bar)
        self.__tickersValidation += 1
        print(self.__tickersValidation)

    def initTickersList(self):
        possibleTickers = getTickers()
        id = 0
        for ticker in possibleTickers:
            contract = Contract()
            contract.symbol = ticker
            contract.secType = "STK"
            contract.exchange = "SMART"
            self.reqContractDetails(id, contract)
            id += 1
        self.__tickersProgress = id

    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        super().contractDetails(reqId, contractDetails)
        self.__tickers.setdefault(contractDetails.contract.symbol, contractDetails.contract.conId)
        self.__tickersValidation += 1
        print(self.__tickersValidation)

    def isLoading(self):
        return self.__tickersValidation != self.__tickersProgress

app = TestApp()

def runApp():
    app.connect('127.0.0.1', 7496, 0)
    app.run()

if __name__ == '__main__':
    t = Thread(target=runApp)
    t.start()
    