import sys
import traceback
import pyuac

from PySide6.QtWidgets import QApplication,QStyleFactory
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from systems import cacheController
from systems import configController
from utilities import utils
from utilities import workMode
from widgets import watcherWindow

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    utils.logError(tb)

def setupGui(app):
    app.setStyle(QStyleFactory.create('Fusion'))
    app.setApplicationName(' ')
    icon = QPixmap(32, 32)
    icon.fill(Qt.GlobalColor.transparent)
    app.setWindowIcon(icon)

def main():
    utils.log('====================== PROGRAMM STARTED ======================')
    utils.logError('====================== PROGRAMM STARTED ======================')

    workMode.setupWorkMode('STOCK')

    if len(sys.argv) > 1:
        workMode.setupWorkMode(sys.argv[1])
    cacheController.load()
    configController.load()
    
    sys.excepthook = excepthook
    app = QApplication([])
    setupGui(app)
    watcherWindow.window = watcherWindow.WatcherWindow()
    watcherWindow.window.show()
    result = app.exec()
    sys.exit(result)

if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        main()

    # import cProfile as profile
    # import pstats

    # prof = profile.Profile()
    # prof.enable()

    # prof.disable()
    # stats = pstats.Stats(prof).strip_dirs().sort_stats("cumtime")
    # stats.print_stats(10) # top 10 rows
        
# to do check channel settings

# to do channel visualize (remove union may be then)
# to do can improve channel calculate if store next max/min prices in candle?
# can check can current ECL cross current min max in future

# move feeController inside tfController, may be cache fee filter results for N days
# fix bored ago calculate, make fixed tf for it, not lowest    
# fix divergence actual length for channels!

# look to actual yfinance multithread lib with less 1d intervals
# fix getFtpNasdaqData, mb save cached result?
        
# рисовать вертикальную линию на 200 свечей?
# добавить количество акций в индикатор
# добавить время закрытия в atr скрипт
# ограничение по цене и размеру позиции в фильтры (atr > 10 Баксов)
# bored учитывает только торговые дни?)


# to do atr new test
# to do divergence test

# to do volume * close price indicator
# сделать индикатор на диверы
# индикатор на трендовые на RSI

# сделать цвета для тикеров по фильтру, интервальных фильтров (без All), вкладок.

# to do auto order open
# to do parse data from orders

# to do add color for tickers, tabs
# to do add price delta for last N filter

# after stock exchange
# to do save atr data | cleanup unused candles?
# to do optimize loop

# to do add root logs handler also for binance logs
