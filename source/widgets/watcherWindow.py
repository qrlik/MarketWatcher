import os
import datetime
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QWidget, QMenuBar, QTextEdit, QFrame, QApplication
from PySide6.QtCore import QFile, QTimer
from PySide6.QtUiTools import QUiLoader

from api import api
from systems import cacheController
from systems import configController
from systems import settingsController
from systems import soundNotifyController
from systems import watcherController
from systems import userDataController

from widgets import configsWindow
from widgets import watcherTable
from widgets import infoWidget
from widgets import menuBar
from utilities import utils

class WatcherWindow(QMainWindow):
    def __init__(self):
        super(WatcherWindow, self).__init__()
        self.__watcherInited = False
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
        self.__logBrowser:QTextEdit = self.__watcherWidget.findChild(QTextEdit, 'logBrowser')
        watcherTable.init(self)
        infoWidget.init(self)
        infoWidget.connectTabsChanged(watcherTable.updateViewedDivergence)

    def __initSizes(self):
        self.setFixedWidth(850)
        self.setFixedHeight(600)
        self.__logBrowser.setFixedHeight(150)

    def __initTimer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.__loop)
        timer.start(settingsController.getSetting('loopInterval'))

    def __loop(self):
        if not self.__watcherInited:
            watcherController.start()
            userDataController.init()
            watcherTable.initList()
            soundNotifyController.init()
            self.__watcherInited = True

        progress = watcherController.loop()
        userDataController.update()
        self.__logProgress(progress)
        watcherTable.update()
        soundNotifyController.update()

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