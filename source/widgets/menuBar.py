from PySide6.QtWidgets import QMenuBar,QMenu
from PySide6.QtGui import QAction

from systems import cacheController
from systems import watcherController

__menuBar:QMenuBar = None
__tools:QMenu = None
__viewAll:QAction = None

def init(bar:QMenuBar):
    global __menuBar
    __menuBar = bar
    __initTools()

def __initTools():
    global __menuBar,__tools,__viewAll
    __tools = __menuBar.addMenu('Tools')
    __viewAll = __tools.addAction('View All')
    __viewAll.triggered.connect(__onToolsViewAll)

def __onToolsViewAll():
    for ticker, tickerController in watcherController.getTickers().items():
        for timeframe, timeframeController in tickerController.getTimeframes().items():
            for divergence in timeframeController.getDivergenceController().getActuals():
                time1 = divergence.firstCandle.time
                time2 = divergence.secondCandle.time
                cacheController.setDivergenceViewed(ticker, timeframe.name, time1, time2, True)
                divergence.viewed = True
    cacheController.save()