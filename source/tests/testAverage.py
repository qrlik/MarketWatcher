from models import candle
from models import movingAverage
from systems import movingAverageController
from utilities import utils

class averageTester:
    def __init__(self, name:str):
        self.name = name
        self.testData = utils.loadJsonFile('assets/tests/' + self.name)
        self.averageController = movingAverageController.MovingAverageController([ movingAverage.MovingAverageType.EMA21 ])
        self.averageController.init(self.testData['precision'])

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

            self.averageController.process(candle)
            if candle.time == self.checks[checkIndex]['time']:
                for type, value in self.averageController.getAverages().items():
                    result &= value == self.checks[checkIndex].get(type.name, 0.0)
                self.__checkError(result, checkIndex)
                checkIndex += 1

        result &= checkIndex == self.checksAmount
        if result:
            utils.log(self.name + ' OK')
        else:
            utils.logError(self.name + ' FAILED')

def test():
    averageTester('testAverage1').test()