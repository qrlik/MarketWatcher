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
from systems import soundNotifyController
from systems import watcherController
from systems import userDataController
from widgets.watcherTableItems import tickerNameItem
from widgets.watcherTableItems import divergenceAccumulatePowerItem
from widgets.watcherTableItems import divergenceBearPowerItem
from widgets.watcherTableItems import divergenceBullPowerItem
from widgets import configsWindow
from widgets import infoWidget
from widgets import menuBar
from utilities import utils

class WatcherWindow(QMainWindow):
    def __init__(self):
        super(WatcherWindow, self).__init__()
        self.__watcherInited = False
        self.__sortColumn = 1
        self.__lastProgress = -1

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
        bar = self.findChild(QMenuBar, 'menuBar')
        self.setMenuBar(bar)
        menuBar.init(bar)

        self.__initTimer()

    def __loadUi(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "../ui/watcherWindow.ui")
        uiFile = QFile(path)
        uiFile.open(QFile.ReadOnly)
        loader.load(uiFile, self)
        uiFile.close()

    # def __initConfigWindow(self):
    #     self.__configsWindow = configsWindow.ConfigsWindow()
    #     self.setCentralWidget(self.__configsWindow)
    #     self.__configsWindow.onStart.connect(self.__onStart)

    def __onStart(self):
        self.__init()

        ##
        #self.__configsWindow.close()
        #self.__configsWindow = None

    def __initValues(self):
        self.__watcherWidget:QWidget = self.findChild(QWidget, 'watcherWidget')
        self.__watcherTable:QTableWidget = self.__watcherWidget.findChild(QTableWidget, 'watcherTable')
        self.__infoWidget:QFrame = self.__watcherWidget.findChild(QFrame, 'infoWidget')
        self.__logBrowser:QTextEdit = self.__watcherWidget.findChild(QTextEdit, 'logBrowser')
        infoWidget.setWidget(self.__infoWidget)
        infoWidget.connectTabsChanged(self.__updateViewedDivergence)

    def __initList(self):
        self.__watcherTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.__watcherTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.__watcherTable.itemSelectionChanged.connect(self.__updateInfoWidget)
        tickers = watcherController.getTickers().keys()
        self.__watcherTable.setRowCount(len(tickers))
        self.__watcherTable.setColumnCount(4)
        self.__watcherTable.setHorizontalHeaderLabels(['Ticker', 'Power', 'Bull Power,%', 'Bear Power,%'])
        self.__watcherTable.horizontalHeader().sectionClicked.connect(self.__updateSortOrder)

        row = 0
        for ticker in tickers:
            self.__watcherTable.setItem(row, 0, tickerNameItem.TickerNameItem(ticker))
            self.__watcherTable.setItem(row, 1, divergenceAccumulatePowerItem.DivergenceAccumulatePowerItem(ticker))
            self.__watcherTable.setItem(row, 2, divergenceBullPowerItem.DivergenceBullPowerItem(ticker))
            self.__watcherTable.setItem(row, 3, divergenceBearPowerItem.DivergenceBearPowerItem(ticker))
            row += 1

    def __initSizes(self):
        self.setFixedWidth(1025)
        self.setFixedHeight(600)
        self.__infoWidget.setFixedWidth(550)
        self.__logBrowser.setFixedHeight(150)

    def __initTimer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.__loop)
        timer.start(settingsController.getSetting('loopInterval'))

    def __loop(self):
        if not self.__watcherInited:
            watcherController.start()
            userDataController.init()
            self.__initList()
            soundNotifyController.init()
            self.__watcherInited = True

        progress = watcherController.loop()
        userDataController.update()
        self.__logProgress(progress)
        self.__updateList()
        self.__updateInfoWidget(False)
        soundNotifyController.update()

    def __updateViewedDivergence(self):
        selectedItems = self.__watcherTable.selectedItems()
        if len(selectedItems) == 0:
            return
        selectedItems[1].update()

    def __updateInfoWidget(self, byClick=True):
        selectedItems = self.__watcherTable.selectedItems()
        if len(selectedItems) == 0:
            return
        infoWidget.update(selectedItems[0].getTicker(), byClick)
    
    def __updateSortOrder(self, index):
        if index != self.__sortColumn and (index == 0 or index == 1):
            self.__sortColumn = index
            self.__sortList()

    def __updateList(self):
        for r in range(self.__watcherTable.rowCount()):
            for c in range(0, self.__watcherTable.columnCount()):
                self.__watcherTable.item(r, c).update()
        self.__sortList()

    def __sortList(self):
        if self.__sortColumn == 0:
            self.__watcherTable.sortItems(self.__sortColumn, order = Qt.SortOrder.AscendingOrder)
        elif self.__sortColumn == 1:
            self.__watcherTable.sortItems(self.__sortColumn, order = Qt.SortOrder.DescendingOrder)

    def __isLoaded(self):
        return self.__lastProgress >= 100

    def __logProgress(self, progress):
        if self.__isLoaded() or self.__lastProgress >= progress:
            return
        text = '...' + (str(progress) if progress < 100 else 'ALL LOADED')
        self.__logBrowser.insertPlainText(text)
        self.__lastProgress = progress

    def closeEvent(self, event):
        watcherController.saveData()
        cacheController.save()
        api.atExit()
        QApplication.exit(0)
        return super().closeEvent(event)

    def log(self, text:str):
        if not self.__logBrowser:
            return
        self.__logBrowser.append(datetime.datetime.now().strftime("%H:%M:%S") + ': ' + text)
        self.__logBrowser.verticalScrollBar().setValue(self.__logBrowser.verticalScrollBar().maximum())