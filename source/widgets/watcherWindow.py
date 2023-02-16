import os
import datetime
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QMenuBar, QTextEdit
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from widgets import configsWindow
from utilities import utils

class WatcherWindow(QMainWindow):
    def __init__(self):
        super(WatcherWindow, self).__init__()

        self.__initConfigWindow()
        #self.__onStart()

    def __loadUi(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "../ui/watcherWindow.ui")
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

        self.__initValues()
        self.setCentralWidget(self.__watcherWidget)
        self.setMenuBar(self.findChild(QMenuBar, 'menuBar'))

        ##
        self.__configsWindow.close()
        self.__configsWindow = None

    def __initValues(self):
        self.__watcherWidget = self.findChild(QWidget, 'watcherWidget')
        if self.__watcherWidget:
            self.__logBrowser = self.__watcherWidget.findChild(QTextEdit, 'logBrowser')

    def log(self, text:str):
        if not self.__logBrowser:
            return
        self.__logBrowser.append(datetime.datetime.now().strftime("%H:%M:%S") + ': ' + text)
        utils.log(text)

    __configsWindow:QWidget = None
    __watcherWidget:QWidget = None
    __logBrowser:QTextEdit = None