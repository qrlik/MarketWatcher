
from PySide6.QtCore import QThread
from threading import Lock
#import debugpy # Uncomment the next line to import debugpy for debugging this thread
import asyncio

from api import apiLimits
from widgets import watcherWindow

class ApiRequests(QThread):
    def __init__(self):
        super().__init__()
        self.__newTasks = []
        self.__tasksAmount = 0
        self.__taskLock = Lock()

        self.__responces = {}
        self.__responceLock = Lock()

        self.__requestCounter = 0
        self.__responseCounter = 0
        self.__loop = asyncio.new_event_loop()

    def run(self):
        #debugpy.debug_this_thread()
        watcherWindow.window.log('Start request server data')
        asyncio.set_event_loop(self.__loop)
        self.__loop.call_soon_threadsafe(self.__processTasks)
        self.__loop.run_forever()

    async def __requestTask(self, id, callback, *args):
        result = await callback(*args)
        with self.__responceLock:
            self.__responces.setdefault(id, result)
        with self.__taskLock:
            self.__tasksAmount -= 1

    def __processTasks(self):
        newTasksAmount = len(self.__newTasks)
        allowedAmount = apiLimits.getAllowedAmount() - self.__tasksAmount
        if allowedAmount >= newTasksAmount:
            with self.__taskLock:
                self.__tasksAmount += newTasksAmount
                for task in self.__newTasks:
                    self.__loop.create_task(self.__requestTask(task[0], task[1], *task[2]))
                self.__newTasks.clear()
        else:
            self.__loop.call_soon_threadsafe(self.__processTasks)
        
    def addAsyncRequest(self, callback, *args):
        requestId = self.__requestCounter
        with self.__taskLock:
            self.__requestCounter += 1
            self.__newTasks.append((requestId, callback, args))
        if self.__loop.is_running():
            self.__loop.call_soon_threadsafe(self.__processTasks)
        return requestId

    def getResponse(self, id):
        result = self.__responces.get(id, None)
        if result is not None:
            with self.__responceLock:
                self.__responseCounter += 1
                self.__responces.pop(id)
        return result
    
    def getProgress(self):
        return int(self.__responseCounter / self.__requestCounter * 100) if self.__requestCounter > 0 else 0

requester = ApiRequests()