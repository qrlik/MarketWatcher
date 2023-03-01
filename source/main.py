import sys
from PySide6.QtWidgets import QApplication

from widgets import watcherWindow
from systems import watcherController

if __name__ == "__main__":
    app = QApplication([])
    widget = watcherWindow.WatcherWindow()
    widget.show()
    sys.exit(app.exec())

# to do
# to do save closed candles on new finished candle