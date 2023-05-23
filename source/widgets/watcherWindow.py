import os
import datetime
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QMenuBar, QTextEdit, QTableWidget, QTableWidgetItem, QFrame, QAbstractItemView, QApplication
from PySide6.QtCore import QFile, QTimer, Qt
from PySide6.QtUiTools import QUiLoader

from api import api
from systems import cacheController
from systems import configController
from systems import settingsController
from systems import watcherController
from widgets.watcherTableItems import divergenceAccumulatePowerItem
from widgets.watcherTableItems import divergenceBearPowerItem
from widgets.watcherTableItems import divergenceBullPowerItem
from widgets import configsWindow
from widgets import infoWidget
from utilities import utils

class WatcherWindow(QMainWindow):
    def __init__(self):
        super(WatcherWindow, self).__init__()

        configController.load('default')#(cacheController.getLastConfigFilename())
        #self.__initConfigWindow()
        self.__onStart()
        utils.addLogListener(self)

    def __del__(self):
        utils.deleteLogListener(self)

    def __init(self):
        self.__loadUi()
        self.__initValues()
        self.__initSizes()

        self.setCentralWidget(self.__watcherWidget)
        #self.setMenuBar(self.findChild(QMenuBar, 'menuBar'))

        watcherController.start()
        self.__initList()
        self.__initTimer()

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
        #self.__configsWindow.close()
        #self.__configsWindow = None

    def __initValues(self):
        self.__watcherWidget = self.findChild(QWidget, 'watcherWidget')
        self.__watcherTable:QTableWidget = self.__watcherWidget.findChild(QTableWidget, 'watcherTable')
        self.__infoWidget = self.__watcherWidget.findChild(QFrame, 'infoWidget')
        self.__logBrowser = self.__watcherWidget.findChild(QTextEdit, 'logBrowser')
        infoWidget.setWidget(self.__infoWidget)

    def __initList(self):
        self.__watcherTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.__watcherTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.__watcherTable.itemSelectionChanged.connect(self.__updateInfoWidget)
        tickers = watcherController.getTickers().keys()
        self.__watcherTable.setRowCount(len(tickers))
        self.__watcherTable.setColumnCount(4)
        self.__watcherTable.setHorizontalHeaderLabels(['Ticker', 'Power', 'Bull Power', 'Bear Power'])
        row = 0
        for ticker in tickers:
            self.__watcherTable.setItem(row, 0, QTableWidgetItem(ticker))
            self.__watcherTable.setItem(row, 1, divergenceAccumulatePowerItem.DivergenceAccumulatePowerItem(ticker))
            self.__watcherTable.setItem(row, 2, divergenceBullPowerItem.DivergenceBullPowerItem(ticker))
            self.__watcherTable.setItem(row, 3, divergenceBearPowerItem.DivergenceBearPowerItem(ticker))
            row += 1

    def __initSizes(self):
        self.setFixedWidth(1100)
        self.setFixedHeight(600)
        self.__infoWidget.setFixedWidth(625)
        self.__logBrowser.setFixedHeight(150)

    def __initTimer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.__loop)
        timer.start(settingsController.getSetting('loopInterval'))

    def __loop(self):
        watcherController.loop()
        self.__updateList()
        self.__updateInfoWidget()

    def __updateInfoWidget(self):
        selectedItems = self.__watcherTable.selectedItems()
        if len(selectedItems) == 0:
            return
        infoWidget.update(selectedItems[0].text())
            
    def __updateList(self):
        #to do is any dirty
        for r in range(self.__watcherTable.rowCount()):
            for c in range(1, self.__watcherTable.columnCount()):
                self.__watcherTable.item(r, c).update()
        self.__watcherTable.sortItems(1, order = Qt.SortOrder.DescendingOrder)

    def closeEvent(self, event):
        api.atExit()
        QApplication.exit(0)
        return super().closeEvent(event)

    def log(self, text:str):
        if not self.__logBrowser:
            return
        self.__logBrowser.append(datetime.datetime.now().strftime("%H:%M:%S") + ': ' + text)