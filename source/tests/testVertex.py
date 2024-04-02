from models import timeframe
from systems import vertexController
from systems import candlesController
from utilities import utils

class vertexTester:
    def __init__(self, name:str):
        self.name = name
        self.testData = utils.loadJsonFile(utils.assetsFolder + 'tests/' + self.name)

        self.candlesController = candlesController.CandlesController(timeframe.Timeframe.ONE_DAY)
        self.candlesController.init('', self.testData['candlesFileName'], self.testData['precision'])
        
        self.vertexController = vertexController.VertexController()
        self.vertexController.init(self.candlesController)

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
        self.vertexController.process()

        for candle in candles:
            if self.checksAmount == checkIndex:
                break

            if candle.time == self.checks[checkIndex]['time']:
                vertex1 = candle.vertexClose
                vertex2 = self.checks[checkIndex].get('vertex', None) # to do Close
                vertex2 = vertexController.VertexType[vertex2] if vertex2 else vertex2

                result &= vertex1 == vertex2

                self.__checkError(result, checkIndex)
                checkIndex += 1

        result &= checkIndex == self.checksAmount
        if result:
            print(self.name + ' OK')
        else:
            print(self.name + ' FAILED')

def test():
    vertexTester('testVertex1').test()