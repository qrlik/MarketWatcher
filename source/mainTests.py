
from tests import testAtr
from tests import testSignals

def testAll():
    testAtr.test()
    testSignals.test()

if __name__ == '__main__':
    testAll()