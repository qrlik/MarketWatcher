from ibapi.client import *
from ibapi.common import ListOfContractDescription, ListOfPriceIncrements, TickerId
from ibapi.wrapper import *
from threading import Thread
from enum import IntEnum
import time

class StepType(IntEnum):
    NONE = 0,
    SEARCH = 1,
    TICK = 2,
    DONE = 3

class CheckApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

        self.__reset()
        self.__step = StepType.NONE
        #self.__startLength = 0
        self.__contractCounter = 0
        self.__lastProgress = 0

        #self.__marketRuleIds = {}
        self.__notFound = set()
        self.__wrongTick = set()
        self.__result = set()

    def checkTickersList(self, possibleTickers):
        id = 0
        for ticker in possibleTickers:
            self.__checkDict.setdefault(id, ticker)
            id += 1
        self.__finalProgress = len(possibleTickers)
        self.__requestNext()

    def __reset(self):
        self.__checkDict = {}
        self.__progress = 0
        self.__finalProgress = 1
        self.__lastProgress = 0

    def __logProgress(self):
        progress = int(self.__progress/self.__finalProgress * 100)
        if progress != self.__lastProgress:
            self.__lastProgress = progress
            print(self.__step.name + ' ' + str(self.__lastProgress))

    def __requestNext(self):
        if self.__step == StepType.NONE:
            self.__step = StepType.SEARCH

        if self.__progress < len(self.__checkDict):
            ticker = self.__checkDict[self.__progress]
            if self.__step == StepType.SEARCH:
                #self.reqMatchingSymbols(self.__progress, self.__checkDict[self.__progress])
                self.__contractCounter = 0
                contract = Contract()
                contract.symbol = ticker
                contract.secType = 'STK'
                contract.currency = 'USD'
                contract.exchange = 'SMART'
                self.reqContractDetails(self.__progress, contract)
            # elif self.__step == StepType.TICK:
            #     self.reqMarketRule(self.__marketRuleIds[ticker])
        else:
            if self.__step == StepType.SEARCH:
                self.__reset()
                self.__step = StepType.DONE
                
                self.__notFound = sorted(list(self.__notFound))
                self.__wrongTick = sorted(list(self.__wrongTick))
                
                #self.checkTickersList(self.__result)
            else:
                self.__wrongTick = sorted(list(self.__wrongTick))
                self.__step = StepType.DONE

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        if errorCode == 200 and reqId >= 0 and reqId < len(self.__checkDict) and self.__step != StepType.NONE and self.__step != StepType.DONE:
            self.__notFound.add(self.__checkDict[reqId])
            self.__progress += 1
            self.__logProgress()
            self.__requestNext()
        else:
            return super().error(reqId, errorCode, errorString)

    # def symbolSamples(self, reqId: int, contractDescriptions: ListOfContractDescription):
    #     found = False
    #     wrongCurrency = True
    #     wrongType = True
    #     expectedSymbol = self.__checkDict[reqId]

    #     for contract in contractDescriptions:
    #         contract = contract.contract
    #         symbol = contract.symbol
    #         if symbol != expectedSymbol:
    #             continue
    #         found = True
    #         if contract.currency == 'USD':
    #             wrongCurrency = False
    #         if contract.secType == 'STK':
    #             wrongType = False
              
    #     if not found:
    #         self.__notFound.add(expectedSymbol)
    #     elif wrongCurrency:
    #         self.__wrongCurrency.add(expectedSymbol)
    #     elif wrongType:
    #         self.__wrongType.add(expectedSymbol)
    #     else:
    #         self.__result.add(expectedSymbol)

    #     self.__progress += 1
    #     self.__logProgress()
    #     self.__requestNext()
    #     return super().symbolSamples(reqId, contractDescriptions)

    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        self.__contractCounter += 1
        super().contractDetails(reqId, contractDetails)
        expectedSymbol = self.__checkDict[reqId]
        symbol = contractDetails.contract.symbol
        if expectedSymbol != symbol:
            print('contractDetails expect - ' + expectedSymbol + ' but got - ' + symbol)
            return

        if contractDetails.minTick < 0.01:
            self.__wrongTick.add(symbol)
        else:
            self.__result.add(symbol)

        # ruleIds = contractDetails.marketRuleIds.split(',')
        # exchanges = contractDetails.validExchanges.split(',')
        # try:
        #     exchangeIndex = exchanges.index('SMART')
        #     ruleId = ruleIds[exchangeIndex]
        #     if not ruleId.isnumeric():
        #         raise Exception()
        #     self.__marketRuleIds.setdefault(symbol, int(ruleId))
        #     self.__result.add(symbol)
        # except:
        #     print('contractDetails cant parse market rule id - ' + symbol)
    
    def contractDetailsEnd(self, reqId: int):
        if self.__contractCounter > 1:
            print('contractDetailsEnd more than one - ' + self.__checkDict[reqId])

        self.__progress += 1
        self.__logProgress()
        self.__requestNext()
        return super().contractDetailsEnd(reqId)
    
    # def marketRule(self, marketRuleId: int, priceIncrements: ListOfPriceIncrements):
    #     x = 5

    #     self.__progress += 1
    #     self.__logProgress()
    #     self.__requestNext()
    #     return super().marketRule(marketRuleId, priceIncrements)

    def isLoading(self):
        return self.__step != StepType.DONE
    
    def getInvalidTickers(self):
        result = {}
        #result.setdefault('startLength', len(self.__startLength))
        result.setdefault('notFound', self.__notFound)
        result.setdefault('wrongTick', self.__wrongTick)
        return result
    
def __runApp():
    app.connect('127.0.0.1', 7496, 0)
    app.run()

app = CheckApp()

def runApp():
    thread = Thread(target=__runApp)
    thread.start()
    time.sleep(5)

def exitApp():
    app.disconnect()
    
if __name__ == '__main__':
    runApp()
    app.checkTickersList(['CLOV'])
    while app.isLoading():
        pass
    x = 5