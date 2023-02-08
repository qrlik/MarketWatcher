import os
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QMenuBar
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from widgets import configsWindow

class WatcherWindow(QMainWindow):
    def __init__(self):
        super(WatcherWindow, self).__init__()
        self.__initConfigWindow()

    def __loadUi(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "../watcherWindow.ui")
        uiFile = QFile(path)
        uiFile.open(QFile.ReadOnly)
        loader.load(uiFile, self)
        uiFile.close()

    def __initConfigWindow(self):
        self.__configsWindow = configsWindow.ConfigsWindow()
        self.setCentralWidget(self.__configsWindow)
        self.__configsWindow.onStart.connect(self.__onStart)

    def __onStart(self):
        self.__loadUi()

        self.__watcherWidget = self.findChild(QWidget, 'watcherWidget')
        self.setCentralWidget(self.__watcherWidget)
        self.setMenuBar(self.findChild(QMenuBar, 'menuBar'))

        self.__configsWindow.close()
        self.__configsWindow = None

    __configsWindow:QWidget = None
    __watcherWidget:QWidget = None