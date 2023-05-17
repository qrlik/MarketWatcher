
from tests import testAtr
from tests import testRsi
from tests import testVertex
from tests import testSignals

def testAll():
    testAtr.test()
    testRsi.test()
    testVertex.test()
    #testSignals.test()

if __name__ == '__main__':
    testAll()