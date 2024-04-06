import os
import datetime
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QTextEdit, QApplication, QProgressBar
from PySide6.QtCore import QFile, QTimer
from PySide6.QtUiTools import QUiLoader

from api import api
from api import apiRequests
from systems import cacheController
from systems import configController
from systems import loaderController
from systems import settingsController
from systems import soundNotifyController
from systems import userDataController
from systems import watcherController

from widgets import configsWindow
from widgets.filters import filterWidget
from widgets import watcherTable
from widgets import infoWidget
from utilities import utils
from utilities import workMode

class WatcherWindow(QMainWindow):
    def __init__(self):
        super(WatcherWindow, self).__init__()

        self.__dataDirty = False
        #self.__initConfigWindow()
        self.__onStart()
        utils.addLogListener(self)

    def __init(self):
        self.__loadUi()
        self.__initValues()
        self.__initSizes()

        self.setCentralWidget(self.__watcherWidget)
        self.__initTimer()
        self.__initLoad()

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
        self.__loadedLogged = False
        self.__watcherWidget:QWidget = self.findChild(QWidget, 'watcherWidget')
        self.__logBrowser:QTextEdit = self.__watcherWidget.findChild(QTextEdit, 'logBrowser')
        self.__progressBar:QProgressBar = self.__watcherWidget.findChild(QProgressBar, 'progressBar')
        filterWidget.init(self)
        watcherTable.init(self)
        infoWidget.init(self)

    def __initSizes(self):
        self.setFixedWidth(800)
        self.setFixedHeight(700)
        self.__logBrowser.setFixedHeight(150)

    def __initTimer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.__loop)
        timer.start(settingsController.getSetting('loopInterval'))

    def __initLoad(self):
        self.log('Start load tickers')
        loaderController.startLoad()

    def __loop(self):
        self.__dataDirty |= watcherController.loop()
        self.__updateProgressBar()
        if self.__dataDirty and self.__loadedLogged:
            watcherTable.update() # list will not be updated for crypto runtime changes from websocket
            self.__dataDirty = False
        userDataController.update()
        soundNotifyController.update()

    def __updateProgressBar(self):
        if not loaderController.isDone():
            self.__progressBar.setValue(loaderController.getProgress())
            return
        
        progress = apiRequests.requester.getProgress()
        if progress >= 0 and progress < 100:
            self.__progressBar.setValue(progress)
        elif not self.__loadedLogged: # -1 or 100

            if not loaderController.isValid() or progress < 0:
                self.log('Nothing to request')
            else:
                cacheController.saveCandles()
                cacheController.saveLastCandlesCheck()

                self.log('Ready')
                
            self.__loadedLogged = True
            self.__progressBar.setVisible(False)

    def closeEvent(self, event):
        cacheController.save()
        cacheController.saveCandles()

        apiRequests.requester.quit()
        loaderController.forceQuit()
        
        api.atExit()
        QApplication.exit(0)
        return super().closeEvent(event)

    def log(self, text:str):
        if not self.__logBrowser:
            return
        self.__logBrowser.append(text)
        self.__logBrowser.verticalScrollBar().setValue(self.__logBrowser.verticalScrollBar().maximum())

window = None