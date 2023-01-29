import sys
from PySide6.QtWidgets import QApplication

from widgets import mainWindow

if __name__ == "__main__":
    app = QApplication([])
    widget = mainWindow.MainWindow()
    widget.show()
    sys.exit(app.exec())

# to do
# добавить сохранение последних используемых настроек