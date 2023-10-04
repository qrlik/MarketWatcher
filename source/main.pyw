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

# to do atr new test
# to do divergence test



#   File "d:\stockExchange\MarketWatcher\source\systems\loaderController.py", line 38, in __onLoadFinish
#     watcherTable.initList()
#   File "d:\stockExchange\MarketWatcher\source\widgets\watcherTable.py", line 51, in initList
#     __watcherTable.setRowCount(len(tickers))
#   File "d:\stockExchange\MarketWatcher\source\systems\loaderController.py", line 25, in run
#     tickers = watcherController.requestTickers()
#               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "d:\stockExchange\MarketWatcher\source\systems\watcherController.py", line 17, in requestTickers
#     return api.getTickersList()
#            ^^^^^^^^^^^^^^^^^^^^
#   File "d:\stockExchange\MarketWatcher\source\api\api.py", line 30, in getTickersList
#     return stocks.getTickersList()
#            ^^^^^^^^^^^^^^^^^^^^^^^
#   File "d:\stockExchange\MarketWatcher\source\api\stocks.py", line 46, in getTickersList
#     nasdaq = yahoo.tickers_nasdaq()
#              ^^^^^^^^^^^^^^^^^^^^^^
#   File "d:\stockExchange\MarketWatcher\source\api\third_party\yahoo.py", line 238, in tickers_nasdaq
#     ftp = ftplib.FTP("ftp.nasdaqtrader.com")
#           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "D:\dev\python\Lib\ftplib.py", line 121, in __init__
#     self.connect(host)
#   File "D:\dev\python\Lib\ftplib.py", line 158, in connect
#     self.sock = socket.create_connection((self.host, self.port), self.timeout,
#                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "D:\dev\python\Lib\socket.py", line 851, in create_connection
#     raise exceptions[0]
#   File "D:\dev\python\Lib\socket.py", line 836, in create_connection
#     sock.connect(sa)
# ConnectionRefusedError: [WinError 10061] Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение
#     Note: This exception was delayed.


# add stock full name display

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

# 527ERROR:root:Lost connection to Server. Reason: [Failure instance: Traceback (failure with no frames): <class 'twisted.internet.error.ConnectionAborted'>: Connection was aborted locally using 
# ITCPTransport.abortConnection.
# ]. Retrying: 1

# ERROR:root:Lost connection to Server. Reason: [Failure instance: Traceback (failure with no frames): <class 'twisted.internet.error.ConnectionAborted'>: Connection was aborted locally using ITCPTransport.abortConnection.
# ]. Retrying: 1
# 527
# 527ERROR:root:Lost connection to Server. Reason: [Failure instance: Traceback (failure with no frames): <class 'twisted.internet.error.ConnectionAborted'>: Connection was aborted locally using 
# ITCPTransport.abortConnection.
# ]. Retrying: 1

# maintance
# (403, None, 'https://api.binance.com/api/v3/klines\n{\'symbol\': \'TLMUSDT\', \'interval\': \'1h\', \'startTime\': 1685281485538, \'limit\': 44}
# <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
# <HTML><HEAD><META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
# <TITLE>ERROR: The request could 
# not be satisfied</TITLE>\n</HEAD><BODY>\n<H1>403 ERROR</H1>\n<H2>The request could not be satisfied.</H2>
# <HR noshade size="1px">\nRequest blocked.\nWe can\'t connect to the server for this app or website at this time.
# There might be too much traffic or a configuration error. Try again later, or contact the app or website owner.
# <BR clear="all">\nIf you provide content to customers through CloudFront, you can find steps to troubleshoot and help prevent this error 
# by reviewing the CloudFront documentation.\n<BR clear="all">\n<HR noshade size="1px">\n<PRE>\nGenerated by cloudfront (CloudFront)
# Request ID: -wFQ0oHeDNCwIa0DQFEBmkDZUxxCIe_DrAF91E52mNGy9ksfctMLWA==\n</PRE>\n<ADDRESS>\n</ADDRESS>\n</BODY></HTML>',
#  <CIMultiDictProxy('Server': 'CloudFront', 'Date': 'Tue, 30 May 2023 09:45:42 GMT', 'Content-Type': 'text/html', 'Content-Length': '919',
#  'Connection': 'keep-alive', 'X-Cache': 'Error from cloudfront', 'Via': '1.1 ce90704f6d2bc1f19459aaf24b07365e.cloudfront.net (CloudFront)',
#  'X-Amz-Cf-Pop': 'SOF50-P1', 'X-Amz-Cf-Id': '-wFQ0oHeDNCwIa0DQFEBmkDZUxxCIe_DrAF91E52mNGy9ksfctMLWA==')>)