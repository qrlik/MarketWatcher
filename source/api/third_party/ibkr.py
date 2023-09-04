from ibapi.client import *
from ibapi.common import TickerId
from ibapi.wrapper import *
from threading import Thread
from enum import IntEnum
import time
import json

class StepType(IntEnum):
    NONE = 0,
    SEARCH = 1,
    MARKET_RULE = 2,
    DONE = 3

class CheckApp(EWrapper, EClient):
    __correctRules = []
    __wrongRules = []

    def __init__(self):
        EClient.__init__(self, self)

        self.__loadData()
        self.__reset()
        self.__step = StepType.NONE
        self.__contractCounter = 0
        self.__lastProgress = 0

        self.__backetInfo = {}

        self.__data = {}
        self.__exceptions = {}
        self.__ruleIdsData = {}
        self.__ruleIds = set()

    def __loadData(self):
        try:
            with open('assets/ibkrExceptions.json') as infile:
                data =  json.load(infile)
                self.__correctRules = data.get('correctRules', [])
                self.__wrongRules = data.get('wrongRules', [])
        except:
            return

    def __checkTicker(self, contractDetails: ContractDetails):
        for wrongRule in self.__wrongRules:
            stockType = wrongRule.get('stockType', contractDetails.stockType)
            industry = wrongRule.get('industry', contractDetails.industry)
            category = wrongRule.get('category', contractDetails.category)
            if contractDetails.stockType == stockType \
                and contractDetails.industry == industry \
                and contractDetails.category == category:
                return False
        for correctRule in self.__correctRules:
            stockType = correctRule.get('stockType', contractDetails.stockType)
            industry = correctRule.get('industry', contractDetails.industry)
            category = correctRule.get('category', contractDetails.category)
            if contractDetails.stockType == stockType \
                and contractDetails.industry == industry \
                and contractDetails.category == category:
                return True
        print('contractDetails unknown type - ' + contractDetails.stockType + ' for ' + contractDetails.contract.symbol)
        return False

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

        progress = len(self.__ruleIds) if self.__step == StepType.MARKET_RULE else len(self.__checkDict)
        if self.__progress < progress:
            if self.__step == StepType.SEARCH:
                self.__contractCounter = 0
                contract = Contract()
                contract.symbol = self.__checkDict[self.__progress]
                contract.secType = 'STK'
                contract.currency = 'USD'
                contract.exchange = 'SMART'
                self.reqContractDetails(self.__progress, contract)
            elif self.__step == StepType.MARKET_RULE:
                self.reqMarketRule(self.__ruleIds[self.__progress])
        else:
            if self.__step == StepType.SEARCH:
                self.__reset()
                self.__step = StepType.MARKET_RULE
                self.__finalProgress = len(self.__ruleIds)
                
                for _, arr in self.__exceptions.items():
                    arr = sorted(arr)
                self.__ruleIds = sorted(list(self.__ruleIds))
                self.__requestNext()
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
        if self.__checkTicker(contractDetails):
            data = []
            data.append(contractDetails.longName)
            data.append(stockType)
            data.append(contractDetails.industry)
            data.append(contractDetails.category)
            ruleId = self.__getRuleId(contractDetails)
            data.append(ruleId)
            self.__ruleIds.add(ruleId)
            self.__ruleIdsData.setdefault(ruleId, {})
            self.__data.setdefault(symbol, data)
        else:
            self.__addException(stockType, symbol)

    def contractDetailsEnd(self, reqId: int):
        if self.__contractCounter > 1:
            print('contractDetailsEnd more than one - ' + self.__checkDict[reqId])

        self.__progress += 1
        self.__logProgress()
        self.__requestNext()
        return super().contractDetailsEnd(reqId)
    
    def marketRule(self, marketRuleId: int, priceIncrements: ListOfPriceIncrements):
        rules = {}
        for increment in priceIncrements:
            rules.setdefault(increment.lowEdge, increment.increment)
        rules = dict(sorted(rules.items(), reverse=True))

        self.__ruleIdsData[marketRuleId] = rules
        self.__progress += 1
        self.__logProgress()
        self.__requestNext()
        return super().marketRule(marketRuleId, priceIncrements)

    def isLoading(self):
        return self.__step != StepType.DONE
    
    def getFinalData(self):
        result = {}
        result.setdefault('ruleIds', dict(sorted(self.__ruleIdsData.items())))
        result.setdefault('data', dict(sorted(self.__data.items())))
        result.setdefault('exceptions', dict(sorted(self.__exceptions.items())))
        result.setdefault('backets', dict(sorted(self.__backetInfo.items())))
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

    try:
        with open('test.json', 'w') as outfile:
            json.dump(x, outfile)
    except:
        pass