import sys
import traceback
from PySide6.QtWidgets import QApplication

from utilities import utils
from widgets import watcherWindow

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    utils.logError(tb)

if __name__ == "__main__":
    utils.log('====================== PROGRAMM STARTED ======================')
    utils.logError('====================== PROGRAMM STARTED ======================')
    
    sys.excepthook = excepthook
    app = QApplication([])
    widget = watcherWindow.WatcherWindow()
    widget.show()
    result = app.exec()
    sys.exit(result)

# to do
# to do add root logs handler also for binance logs
# to do check cache with server script
# to do try to msgspec json load lib
# to do save closed candles on new finished candle