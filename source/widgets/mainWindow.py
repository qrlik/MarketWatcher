import os
from pathlib import Path

from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from widgets import configsWindow
from widgets import watcherWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__loadUi()
        self.__initMainWindow()

    def __loadUi(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "../watcherWindow.ui")
        uiFile = QFile(path)
        uiFile.open(QFile.ReadOnly)
        loader.load(uiFile, self)
        uiFile.close()

    def __createWatcherWindow(self):
        self.__watcherWindow = watcherWindow.WatcherWindow()
        self.setCentralWidget(self.__watcherWindow)
        self.__configsWindow.close()
        self.__configsWindow = None


    def __initMainWindow(self):
        self.__configsWindow = configsWindow.ConfigsWindow()
        self.setCentralWidget(self.__configsWindow)
        self.__configsWindow.onDestroy.connect(self.__createWatcherWindow)

    __configsWindow:QWidget = None
    __watcherWindow:QWidget = None