from ibapi.client import *
from ibapi.common import ListOfContractDescription
from ibapi.wrapper import *
from threading import Thread

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.__unknownContracts = set()
        self.__checkDict = {}
        self.__progress = 0
        self.__finalProgress = 1

    def checkTickersList(self, possibleTickers):
        id = 0
        for ticker in possibleTickers:
            ticker = ticker[0]
            self.__checkDict.setdefault(id, ticker)
            id += 1
        self.__finalProgress = len(possibleTickers)
        self.__requestNext()

    def __requestNext(self):
        if self.__progress < len(self.__checkDict):
            self.reqMatchingSymbols(self.__progress, self.__checkDict[self.__progress])

    def symbolSamples(self, reqId: int, contractDescriptions: ListOfContractDescription):
        found = False
        for contract in contractDescriptions:
            contract = contract.contract
            symbol = contract.symbol
            if symbol != self.__checkDict[reqId] or contract.currency != 'USD' or contract.secType != 'STK':
                continue
            found = True
            break
        
        if not found:
            self.__unknownContracts.add(self.__checkDict[reqId])

        self.__progress += 1
        print(self.__progress/self.__finalProgress * 100)
        self.__requestNext()
        return super().symbolSamples(reqId, contractDescriptions)

    def isLoading(self):
        return self.__progress < self.__finalProgress
    
    def getUnknownTickers(self):
        return list(self.__unknownContracts)

def __runApp():
    app.connect('127.0.0.1', 7496, 0)
    app.run()

app = TestApp()

def runApp():
    thread = Thread(target=__runApp)
    thread.start()

def exitApp():
    app.disconnect()
    