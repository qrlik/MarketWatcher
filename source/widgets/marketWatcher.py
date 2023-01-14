import os
from pathlib import Path

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from widgets import configWidget

class MarketWatcher(QWidget):
    def __init__(self):
        super(MarketWatcher, self).__init__()
        self.loadUi()
        self.initConfigWidget()

    def loadUi(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "../form.ui")
        uiFile = QFile(path)
        uiFile.open(QFile.ReadOnly)
        loader.load(uiFile, self)
        uiFile.close()

    def initConfigWidget(self):
        widget = self.findChild(QWidget, 'configWidget')
        configWidget.init(widget)
        self.setFixedSize(520, 320)