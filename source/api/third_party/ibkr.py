from ibapi.client import *
from ibapi.common import TickerId
from ibapi.wrapper import *
from collections import OrderedDict
from threading import Thread
from enum import IntEnum
import time

class StepType(IntEnum):
    NONE = 0,
    SEARCH = 1,
    TICK = 2,
    DONE = 3

class CheckApp(EWrapper, EClient):
    __correctTypes = ['COMMON', 'ADR', 'REIT', 'MLP', 'NY REG SHRS', 'ROYALTY TRST']
    __wrongTypes = ['UNIT', 'ETN', 'ETF', 'ETP', 'CLOSED-END FUND', 'RIGHT', 'PREFERRED', 'CONVPREFERRED', 'TRACKING STK', 'LTD PART', '']

    def __init__(self):
        EClient.__init__(self, self)

        self.__reset()
        self.__step = StepType.NONE
        self.__contractCounter = 0
        self.__lastProgress = 0

        self.__backetInfo = OrderedDict()

        self.__data = OrderedDict()
        self.__exceptions = OrderedDict()
        self.__ruleIds = set()  # to do info

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
                
                for _, list in self.__exceptions.items():
                    list = sorted(list)
            else:
                self.__step = StepType.DONE

    def __addException(self, name, value):
        self.__exceptions.setdefault(name, []).append(value)

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        if errorCode == 200 and reqId >= 0 and reqId < len(self.__checkDict) and self.__step != StepType.NONE and self.__step != StepType.DONE:
            self.__addException('notFound', self.__checkDict[reqId])
            self.__progress += 1
            self.__logProgress()
            self.__requestNext()
        else:
            return super().error(reqId, errorCode, errorString)

    def __getRuleId(self, contractDetails: ContractDetails):
        ruleIds = contractDetails.marketRuleIds.split(',')
        exchanges = contractDetails.validExchanges.split(',')
        try:
            exchangeIndex = exchanges.index('SMART')
            ruleId = ruleIds[exchangeIndex]
            if not ruleId.isnumeric():
                raise Exception()
            return int(ruleId)
        except:
            print('contractDetails cant parse market rule id - ' + contractDetails.contract.symbol)
            return -1

    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        self.__contractCounter += 1
        super().contractDetails(reqId, contractDetails)
        expectedSymbol = self.__checkDict[reqId]
        symbol = contractDetails.contract.symbol
        if expectedSymbol != symbol:
            print('contractDetails expect - ' + expectedSymbol + ' but got - ' + symbol)
            return

        stockType = contractDetails.stockType
        self.__backetInfo.setdefault(stockType, {}).setdefault(contractDetails.industry, {}).setdefault(contractDetails.category, []).append(symbol)
        if stockType in self.__correctTypes:
            if contractDetails.minTick < 0.01:
                self.__addException('wrongTick', symbol) # to do
            else:
                data = []
                data.append(stockType)
                data.append(contractDetails.industry)
                data.append(contractDetails.category)
                ruleId = self.__getRuleId(contractDetails)
                data.append(ruleId)
                self.__ruleIds.add(ruleId)
                self.__data.setdefault(symbol, data)
        elif stockType in self.__wrongTypes:
            self.__addException(stockType, symbol)
        else:
            print('contractDetails unknown type - ' + stockType + ' for ' + symbol)
            self.__addException(stockType, symbol)

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
    
    def getFinalData(self):
        result = {}
        result.setdefault('ruleIds', sorted(list(self.__ruleIds))) # to do info
        result.setdefault('data', self.__data)
        result.setdefault('exceptions', self.__exceptions)
        result.setdefault('backets', self.__backetInfo)
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
    app.checkTickersList(['CLOV', 'ENERU', 'AAPL'])
    while app.isLoading():
        pass
    x = app.getFinalData()
    y = 5