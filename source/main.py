import sys
from PySide6.QtWidgets import QApplication
from widgets import marketWatcher

if __name__ == "__main__":
    app = QApplication([])
    widget = marketWatcher.MarketWatcher()
    widget.show()
    sys.exit(app.exec())
