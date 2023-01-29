import os
from pathlib import Path

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Signal

from widgets import configsWidget
from widgets import configEditor

class ConfigsWindow(QWidget):
    def __init__(self):
        super(ConfigsWindow, self).__init__()
        self.loadUi()
        self.initConfigWidget()

    def loadUi(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "../configsWindow.ui")
        uiFile = QFile(path)
        uiFile.open(QFile.ReadOnly)
        loader.load(uiFile, self)
        uiFile.close()

    def __onStart(self):
        self.onDestroy.emit()

    def initConfigWidget(self):
        self.__configsWidget = self.findChild(QWidget, 'configsWidget')
        self.__configsEditor = self.findChild(QWidget, 'configEditor')
        configsWidget.init(self.__configsWidget)
        configsWidget.startButton.clicked.connect(self.__onStart)
        configEditor.init(self.__configsEditor, configsWidget.getConfigsList())
        self.setFixedSize(520, 320)

    onDestroy = Signal()
    __configsWidget:QWidget = None
    __configsEditor:QWidget = None
