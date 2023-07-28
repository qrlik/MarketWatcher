
from threading import Lock
from threading import Thread
import asyncio

from api import apiLimits

class ApiRequests(Thread):
    def __init__(self):
        self.__newTasks = []
        self.__tasksAmount = 0
        self.__taskLock = Lock()

        self.__responces = {}
        self.__responceLock = Lock()

        self.__requestCounter = 0
        self.__started = False
        self.__loop = asyncio.new_event_loop()
        super().__init__(target=self.__start, daemon=True)
        super().start()

    def start(self):
        if self.__started:
            return
        self.__started = True
        return super().start()
    
    async def __requestTask(self, id, callback, *args):
        result = await callback(*args)
        with self.__responceLock:
            self.__responces.setdefault(id, result)
        with self.__taskLock:
            self.__tasksAmount -= 1

    def __start(self):
        asyncio.set_event_loop(self.__loop)
        self.__loop.run_forever()

    def __continueLoop(self):
        newTasksAmount = len(self.__newTasks)
        allowedAmount = apiLimits.getAllowedAmount() - self.__tasksAmount
        if allowedAmount >= newTasksAmount:
            with self.__taskLock:
                self.__tasksAmount += newTasksAmount
                for task in self.__newTasks:
                    self.__loop.create_task(self.__requestTask(task[0], task[1], *task[2]))
                self.__newTasks.clear()
        else:
            self.__loop.call_soon_threadsafe(self.__continueLoop)
        
    def addAsyncRequest(self, callback, *args):
        return 0 # to do
        requestId = self.__requestCounter
        self.__requestCounter += 1
        with self.__taskLock:
            self.__newTasks.append((requestId, callback, args))
        self.__loop.call_soon_threadsafe(self.__continueLoop)
        return requestId

    def getResponse(self, id):
        result = self.__responces.get(id, None)
        if result is not None:
            with self.__responceLock:
                self.__responces.pop(id)
        return result
        

requester = ApiRequests()