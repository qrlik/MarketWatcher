from models import timeframe
from systems import vertexController
from systems import candlesController
from utilities import utils

class vertexTester:
    def __init__(self, name:str):
        self.name = name
        self.testData = utils.loadJsonFile('assets/tests/' + self.name)

        self.candlesController = candlesController.CandlesController(timeframe.Timeframe.ONE_DAY)
        self.candlesController.init('', self.testData['candlesFileName'])
        
        self.vertexController = vertexController.VertexController()
        self.vertexController.init(self.candlesController)

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
        self.vertexController.process()
        lastCandle = None
        for candle in candles:
            if self.checksAmount == checkIndex:
                break

            if candle.time == self.checks[checkIndex]['time']:
                vertex1 = candle.vertex
                vertex2 = self.checks[checkIndex].get('vertex', None)
                vertex2 = vertexController.VertexType[vertex2] if vertex2 else vertex2

                result &= vertex1 == vertex2

                self.__checkError(result, checkIndex)
                checkIndex += 1
            lastCandle = candle

        result &= checkIndex == self.checksAmount
        if result:
            utils.log(self.name + ' OK')
        else:
            utils.logError(self.name + ' FAILED')

def test():
    vertexTester('testVertex1').test()