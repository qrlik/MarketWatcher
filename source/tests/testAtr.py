from models import candle
from systems import atrController
from utilities import utils

class atrTester:
    def __init__(self, name:str):
        self.name = name
        self.testData = utils.loadJsonFile('assets/tests/' + self.name)
        self.atrController = atrController.AtrController()
        self.atrController.init(2)
        self.atrController.setSize(self.testData['size'])

        self.checks = self.testData['data']
        self.checksAmount = len(self.checks)

        candles = utils.loadJsonFile('assets/candles/' + self.testData['candlesFileName'])
        self.candles = [candle.createFromDict(c) for c in candles]

    def __checkError(self, result, index):
        if not result:
            utils.logError(self.name + ' ERROR - ' + str(index))
            assert(False)

    def test(self):
        result = True
        result &= len(self.candles) > 0
        result &= self.checksAmount > 0
        self.__checkError(result, -1)

        checkIndex = 0
        for candle in self.candles:
            if self.checksAmount == checkIndex:
                break

            self.atrController.process(candle)
            if candle.time == self.checks[checkIndex]['time']:
                atr1 = self.atrController.getAtr()
                atr2 = self.checks[checkIndex].get('atr', None)
                result &= atr1 == atr2
                self.__checkError(result, checkIndex)
                checkIndex += 1

        result &= checkIndex == self.checksAmount
        if result:
            utils.log(self.name + ' OK')
        else:
            utils.logError(self.name + ' FAILED')

def test():
    atrTester('testAtr1').test()