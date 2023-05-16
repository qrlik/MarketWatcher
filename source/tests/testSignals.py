from models import timeframe
from systems import atrController
from systems import candlesController
from systems import signalController
from utilities import utils

def compareSignals(signals, json):
    result = len(signals) == len(json)
    if not result:
        return result
    for i in range(len(json)):
        result &= signals[i][0].name == json[i]['signal']
        result &= signals[i][1].name == json[i]['direction']
        if not result:
            return result
    return result

class signalTester:
    def __init__(self, name:str):
        self.name = name
        self.testData = utils.loadJsonFile('assets/tests/' + self.name)

        self.atrController = atrController.AtrController()
        self.atrController.init(self.testData['precision'])
        self.atrController.setSize(self.testData['size'])

        self.candlesController = candlesController.CandlesController(timeframe.Timeframe.ONE_DAY)
        self.candlesController.init('', self.testData['candlesFileName'])
        
        self.signalController = signalController.SignalController()
        self.signalController.initTest(self.candlesController)

        self.checks = self.testData['data']
        self.checksAmount = len(self.checks)

    def __checkError(self, result, index):
        if not result:
            utils.logError(self.name + ' ERROR - ' + str(index))
            assert(False)

    def test(self):
        pass
        result = True
        candles = self.candlesController.getFinishedCandles()
        result &= len(candles) > 0
        result &= self.checksAmount > 0
        self.__checkError(result, -1)

        checkIndex = 0
        for candle in candles:
            if checkIndex == self.checksAmount:
                break

            self.atrController.process(candle)
            self.signalController.update(candle)
            if candle.time == self.checks[checkIndex]['time']:
                result &= compareSignals(self.signalController.getSignals(), self.checks[checkIndex]['signals'])
                self.__checkError(result, checkIndex)
                checkIndex += 1

        result &= checkIndex == self.checksAmount
        if result:
            utils.log(self.name + ' OK')
        else:
            utils.logError(self.name + ' FAILED')

def test():
    pass