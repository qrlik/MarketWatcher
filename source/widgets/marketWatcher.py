import os
from pathlib import Path

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from widgets import configsWidget
from widgets import configEditor

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

    def __onStart(self):
        x = 5

    def initConfigWidget(self):
        configsW = self.findChild(QWidget, 'configsWidget')
        configE = self.findChild(QWidget, 'configEditor')
        configsWidget.init(configsW)
        configsWidget.startButton.clicked.connect(self.__onStart)
        configEditor.init(configE, configsWidget.getConfigsList())
        self.setFixedSize(520, 320)
