import sys
import traceback
from PySide6.QtWidgets import QApplication

from utilities import utils
from widgets import watcherWindow

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    utils.logError(tb)

from systems import websocketController
from models import timeframe

if __name__ == "__main__":
    websocketController.start(['BTCUSDT', 'ETHUSDT'], timeframe.Timeframe.ONE_MIN)

    sys.excepthook = excepthook
    app = QApplication([])
    widget = watcherWindow.WatcherWindow()
    widget.show()
    sys.exit(app.exec())

    # candles = api.Spot.getFinishedCandles('BTCUSDT', timeframe.Timeframe.ONE_DAY, 400)
    # d = [candle.__dict__ for candle in candles]
    # utils.saveJsonFile('test', d)

# to do
# to do check cache with server before loading
# to do save closed candles on new finished candle