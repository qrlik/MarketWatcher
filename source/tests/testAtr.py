import path
import sys

directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

from models import candle
from systems import atrController
from utilities import utils

class atrTester:
    def __init__(self, name:str):
        self.name = name
        self.testData = utils.loadJsonFile('assets/tests/' + self.name)
        self.atrController = atrController.AtrController()

        self.checks = self.testData['data']
        self.checksAmount = len(self.checks)

        candles = utils.loadJsonFile('assets/candles/' + self.testData['candlesFileName'])
        self.candles = [candle.createFromDict(c) for c in candles]

    def __checkError(self, result, index):
        if not result:
            utils.logError(self.name + ' ERROR - ' + str(index))

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
                result &= round(self.atrController.getAtr(), 2) == self.checks[checkIndex].get('atr', 0.0)
                self.__checkError(result, checkIndex)
                checkIndex += 1

        result &= checkIndex == self.checksAmount
        if result:
            utils.log(self.name + ' OK')
        else:
            utils.logError(self.name + ' FAILED')

def test():
    atrTester('testAtr1').test()