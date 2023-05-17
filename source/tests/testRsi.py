from models import timeframe
from systems import rsiController
from systems import candlesController
from utilities import utils

class rsiTester:
    def __init__(self, name:str):
        self.name = name
        self.testData = utils.loadJsonFile('assets/tests/' + self.name)

        self.candlesController = candlesController.CandlesController(timeframe.Timeframe.ONE_DAY)
        self.candlesController.init('', self.testData['candlesFileName'])
        
        self.rsiController = rsiController.RsiController()
        self.rsiController.init(self.candlesController)
        self.rsiController.setSize(self.testData['size'])

        self.checks = self.testData['data']
        self.checksAmount = len(self.checks)

    def __checkError(self, result, index):
        if not result:
            utils.logError(self.name + ' ERROR - ' + str(index))
            assert(False)

    def test(self):
        result = True
        candles = self.candlesController.getFinishedCandles()
        result &= len(candles) > 0
        result &= self.checksAmount > 0
        self.__checkError(result, -1)

        checkIndex = 0
        self.rsiController.process()
        for candle in candles:
            if self.checksAmount == checkIndex:
                break

            if candle.time == self.checks[checkIndex]['time']:
                rsi1 = candle.rsi
                rsi2 = self.checks[checkIndex].get('rsi', None)
                result &= rsi1 == rsi2
                self.__checkError(result, checkIndex)
                checkIndex += 1

        result &= checkIndex == self.checksAmount
        if result:
            utils.log(self.name + ' OK')
        else:
            utils.logError(self.name + ' FAILED')

def test():
    rsiTester('testRsi1').test()