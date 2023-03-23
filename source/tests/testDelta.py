import path
import sys

directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

from models import candle
from systems import deltaController
from utilities import utils

class deltaTester:
    def __init__(self, name:str):
        self.name = name
        self.testData = utils.loadJsonFile('assets/tests/' + self.name)
        self.deltaController = deltaController.DeltaController()

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

            self.deltaController.process(candle)
            if candle.time == self.checks[checkIndex]['time']:
                result &= self.deltaController.getPrettyDelta() == self.checks[checkIndex].get('delta', 0.0)
                self.__checkError(result, checkIndex)
                checkIndex += 1

        result &= checkIndex == self.checksAmount
        if result:
            utils.log(self.name + ' OK')
        else:
            utils.logError(self.name + ' FAILED')

def testDelta():
    deltaTester('testDelta1').test()