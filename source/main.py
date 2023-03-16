import sys
import traceback
from PySide6.QtWidgets import QApplication

from utilities import utils
from widgets import watcherWindow

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    utils.logError(tb)

if __name__ == "__main__":
    sys.excepthook = excepthook
    app = QApplication([])
    widget = watcherWindow.WatcherWindow()
    widget.show()
    sys.exit(app.exec())

# to do
# to do save closed candles on new finished candle