from PySide6.QtCore import QThread
#import debugpy # Uncomment the next line to import debugpy for debugging this thread

from api import apiRequests
from api import api
from systems import configController
from systems import soundNotifyController
from systems import userDataController
from systems import watcherController
from systems import websocketController
from widgets import watcherTable
from utilities import utils

class LoadingThread(QThread):
	def __init__(self):
		super().__init__()
		self.fullProgress = 0

	def run(self):
		# Uncomment the next line to enable debugging in this thread
		#debugpy.debug_this_thread()
		api.init()
		soundNotifyController.init()
		userDataController.init()

		try:
			tickers = watcherController.requestTickers()
			socketList = [ticker[0] for ticker in tickers]
			websocketController.start(socketList, configController.getTimeframes())

			self.fullProgress = len(tickers)
			watcherController.loadTickets(tickers)
		except Exception as e:
			utils.logError(str(e))
			self.exit()

__thread = LoadingThread()
__isDone = False
__isValid = True

def __onLoadFinish():
	global __isDone,__isValid,__thread
	__isDone = True
	__isValid = __thread.fullProgress > 0
	watcherTable.initList()
	apiRequests.requester.start()
	__thread.quit()

def forceQuit():
	__thread.quit()

def isDone():
	return __isDone

def isValid():
	return __isValid

def startLoad():
	global __thread
	__thread.finished.connect(__onLoadFinish)
	__thread.start()

def getProgress():
	progressTickers = len(watcherController.getTickers())
	return int(progressTickers / __thread.fullProgress * 100) if __thread.fullProgress > 0 else 0
