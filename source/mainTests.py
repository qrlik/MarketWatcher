
from tests import testAtr
from tests import testRsi
from tests import testSignals

def testAll():
    testAtr.test()
    testRsi.test()
    #testSignals.test()

if __name__ == '__main__':
    testAll()