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
        



# == TO DO LIST ==

# add bored expired color
  
# fix divergence actual length for channels
# fix divergence actual range can show breaked divergences

# look divergences in rsi indicator
# divergence indicator
# divergence test
 


# == if add more intervals ==
# fix bored ago calculate, make fixed tf for it, not lowest  
# look to actual yfinance multithread lib with less 1d intervals
