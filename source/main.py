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

# to do
# to do add root logs handler also for binance logs

#(418, -1003, "https://api.binance.com/api/v3/klines\n{'symbol': 'RVNUSDT', 'interval': '1w', 'startTime': 715902601076, 'limit': 1000}\nWay too much request weight used; IP banned until 1684187513218. Please use WebSocket Streams for live updates to avoid bans.", <CIMultiDictProxy('Content-Type': 'application/json;charset=UTF-8', 'Content-Length': '148', 'Connection': 'keep-alive', 'Date': 'Mon, 15 May 2023 21:50:02 GMT', 'Server': 'nginx', 'x-mbx-uuid': 'ecc234a3-b3db-4b7e-a001-1031716f5a09', 'x-mbx-used-weight': '190', 'x-mbx-used-weight-1m': '190', 'Retry-After': '112', 'Strict-Transport-Security': 'max-age=31536000; includeSubdomains', 'X-Frame-Options': 'SAMEORIGIN', 'X-Xss-Protection': '1; mode=block', 'X-Content-Type-Options': 'nosniff', 'Content-Security-Policy': "default-src 'self'", 'X-Content-Security-Policy': "default-src 'self'", 'X-WebKit-CSP': "default-src 'self'", 'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma': 'no-cache', 'Expires': '0', 'X-Cache': 'Error from cloudfront', 'Via': '1.1 77c9518ff58162b5acfe6c69f9a24ec8.cloudfront.net (CloudFront)', 'X-Amz-Cf-Pop': 'SOF50-P1', 'X-Amz-Cf-Id': 'DOMQfge6-PDF54ohaf3zypxlwz_nCGWzI3duj6KjbYk1a2nXrVUQEw==')>)