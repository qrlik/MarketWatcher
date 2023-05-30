import sys
import traceback
from PySide6.QtWidgets import QApplication

from utilities import utils
from widgets import watcherWindow

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    utils.logError(tb)

if __name__ == "__main__":
    utils.log('====================== PROGRAMM STARTED ======================')
    utils.logError('====================== PROGRAMM STARTED ======================')
    
    sys.excepthook = excepthook
    app = QApplication([])
    widget = watcherWindow.WatcherWindow()
    widget.show()
    result = app.exec()
    sys.exit(result)

    # import cProfile as profile
    # import pstats

    # prof = profile.Profile()
    # prof.enable()

    # prof.disable()
    # stats = pstats.Stats(prof).strip_dirs().sort_stats("cumtime")
    # stats.print_stats(10) # top 10 rows

# to do add markable into cache
# to do break in % from 0 to 100?
# to do add root logs handler also for binance logs
# to do request api system (from thread), every request return requestId, check for exceptions, limits

# WARNING:root:WebSocket connection closed: connection was closed uncleanly ("WebSocket opening handshake timeout (peer did not finish the opening handshake in time)"), code: 1006, clean: False, 
# reason: connection was closed uncleanly ("WebSocket opening handshake timeout (peer did not finish the opening handshake in time)")
# 527ERROR:root:Lost connection to Server. Reason: [Failure instance: Traceback (failure with no frames): <class 'twisted.internet.error.ConnectionAborted'>: Connection was aborted locally using 
# ITCPTransport.abortConnection.
# ]. Retrying: 1

# 527WARNING:root:WebSocket connection closed: connection was closed uncleanly ("WebSocket opening handshake timeout (peer did not finish the opening handshake in time)"), code: 1006, clean: False, reason: connection was closed uncleanly ("WebSocket opening handshake timeout (peer did not finish the opening handshake in time)")

# ERROR:root:Lost connection to Server. Reason: [Failure instance: Traceback (failure with no frames): <class 'twisted.internet.error.ConnectionAborted'>: Connection was aborted locally using ITCPTransport.abortConnection.
# ]. Retrying: 1
# 527
# WARNING:root:WebSocket connection closed: connection was closed uncleanly ("WebSocket opening handshake timeout (peer did not finish the opening handshake in time)"), code: 1006, clean: False, 
# reason: connection was closed uncleanly ("WebSocket opening handshake timeout (peer did not finish the opening handshake in time)")
# 527ERROR:root:Lost connection to Server. Reason: [Failure instance: Traceback (failure with no frames): <class 'twisted.internet.error.ConnectionAborted'>: Connection was aborted locally using 
# ITCPTransport.abortConnection.
# ]. Retrying: 1
#WARNING:root:WebSocket connection closed: connection was closed uncleanly ("peer dropped the TCP connection without previous WebSocket closing handshake"), code: 1006, clean: False, reason: connection was closed uncleanly ("peer dropped the TCP connection without previous WebSocket closing handshake")