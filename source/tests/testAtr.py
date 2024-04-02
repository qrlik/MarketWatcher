from models import timeframe
from systems import atrController
from systems import candlesController
from utilities import utils

class atrTester:
    def __init__(self, name:str):
        self.name = name
        self.testData = utils.loadJsonFile(utils.assetsFolder + 'tests/' + self.name)

        self.candlesController = candlesController.CandlesController(timeframe.Timeframe.ONE_DAY)
        self.candlesController.init('', self.testData['candlesFileName'], self.testData['precision'])
        
        self.atrController = atrController.AtrController()
        self.atrController.init(self.candlesController)
        self.atrController.setSize(self.testData['size'])

        self.checks = self.testData['data']
        self.checksAmount = len(self.checks)

    def __checkError(self, result, index):
        if not result:
            print(self.name + ' ERROR - ' + str(index))
            assert(False)

    def test(self):
        result = True
        candles = self.candlesController.getFinishedCandles()
        result &= len(candles) > 0
        result &= self.checksAmount > 0
        self.__checkError(result, -1)

        checkIndex = 0
        self.atrController.process()
        for candle in candles:
            if self.checksAmount == checkIndex:
                break

            if candle.time == self.checks[checkIndex]['time']:
                atr1 = candle.atr
                atr2 = self.checks[checkIndex].get('atr', None)
                result &= atr1 == atr2
                self.__checkError(result, checkIndex)
                checkIndex += 1

        result &= checkIndex == self.checksAmount
        if result:
            print(self.name + ' OK')
        else:
            print(self.name + ' FAILED')

def test():
    atrTester('testAtr_WMA').test()
    #atrTester('testAtr_EMA').test()