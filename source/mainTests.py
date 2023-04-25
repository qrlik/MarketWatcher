
from tests import testAtr
from tests import testAverage
from tests import testSignals

def testAll():
    testAtr.test()
    testAverage.test()
    testSignals.test()

if __name__ == '__main__':
    testAll()