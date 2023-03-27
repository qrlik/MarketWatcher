import os
import datetime
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QMenuBar, QTextEdit, QListWidget, QFrame, QAbstractItemView
from PySide6.QtCore import QFile, QTimer
from PySide6.QtUiTools import QUiLoader

from models import listTicketItem
from systems import cacheController
from systems import configController
from systems import watcherController
from widgets import configsWindow
from widgets import infoWidget
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
        watcherController.start()
        self.__loadUi()
        self.__initValues()
        self.__initSizes()
        self.__initTimer()
        self.__initList()

        self.setCentralWidget(self.__watcherWidget)
        #self.setMenuBar(self.findChild(QMenuBar, 'menuBar'))
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

        ##
        # self.__configsWindow.close()
        # self.__configsWindow = None

    def __initValues(self):
        self.__watcherWidget = self.findChild(QWidget, 'watcherWidget')
        self.__watcherList = self.__watcherWidget.findChild(QListWidget, 'watcherList')
        self.__infoWidget = self.__watcherWidget.findChild(QFrame, 'infoWidget')
        self.__logBrowser = self.__watcherWidget.findChild(QTextEdit, 'logBrowser')
        infoWidget.setWidget(self.__infoWidget)

    def __initList(self):
        self.__watcherList.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.__watcherList.itemSelectionChanged.connect(self.__updateInfoWidget)
        for ticker, _ in watcherController.getTickers().items():
            self.__watcherList.insertItem(0, listTicketItem.ListTicketItem(ticker))

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
        self.__updateInfoWidget()

    def __updateInfoWidget(self):
        selectedItems = self.__watcherList.selectedItems()
        if len(selectedItems) == 0:
            return
        infoWidget.update(selectedItems[0].getTicker())
            
    def __updateList(self):
        for i in range(self.__watcherList.count()):
            self.__watcherList.item(i).update()
        self.__watcherList.sortItems()

    def log(self, text:str):
        if not self.__logBrowser:
            return
        self.__logBrowser.append(datetime.datetime.now().strftime("%H:%M:%S") + ': ' + text)