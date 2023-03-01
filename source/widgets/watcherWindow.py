import os
import datetime
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QMenuBar, QTextEdit, QListWidget, QTabWidget
from PySide6.QtCore import QFile, QTimer
from PySide6.QtUiTools import QUiLoader

from widgets import configsWindow
from systems import cacheController
from systems import configController
from systems import watcherController
from utilities import utils

class WatcherWindow(QMainWindow):
    def __init__(self):
        super(WatcherWindow, self).__init__()

        configController.load(cacheController.getLastConfigFilename())
        #self.__initConfigWindow()
        self.__onStart()
        utils.addLogListener(self)

    def __del__(self):
        utils.deleteLogListener(self)

    def __init(self):
        self.__loadUi()
        self.__initValues()
        self.__initSizes()
        self.__initTimer()

        self.setCentralWidget(self.__watcherWidget)
        self.setMenuBar(self.findChild(QMenuBar, 'menuBar'))
        self.__loop()

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
        self.__init()

        watcherController.start()
        ##
        # self.__configsWindow.close()
        # self.__configsWindow = None

    def __initValues(self):
        self.__watcherWidget = self.findChild(QWidget, 'watcherWidget')
        self.__watcherList = self.__watcherWidget.findChild(QListWidget, 'watcherList')
        self.__infoWidget = self.__watcherWidget.findChild(QTabWidget, 'infoWidget')
        self.__logBrowser = self.__watcherWidget.findChild(QTextEdit, 'logBrowser')

    def __initSizes(self):
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        self.__infoWidget.setFixedWidth(300)
        self.__logBrowser.setFixedHeight(150)

    def __initTimer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.__loop)
        timer.start(5000)

    def __loop(self):
        self.__updateList()

    def __updateList(self):
        pass

    def log(self, text:str):
        if not self.__logBrowser:
            return
        self.__logBrowser.append(datetime.datetime.now().strftime("%H:%M:%S") + ': ' + text)

    __configsWindow:QWidget = None

    __watcherWidget:QWidget = None
    __watcherList:QListWidget = None
    __infoWidget:QTabWidget = None
    __logBrowser:QTextEdit = None