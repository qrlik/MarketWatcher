from PySide6.QtCore import QEvent, QObject, Slot
from PySide6.QtWidgets import QApplication

import asyncio
from threading import Lock

#https://doc.qt.io/qtforpython-6/examples/example_async_minimal.html

class AsyncHelper(QObject):
    class ReenterQtObject(QObject):
        """ This is a QObject to which an event will be posted, allowing
            asyncio to resume when the event is handled. event.fn() is
            the next entry point of the asyncio event loop. """
        def event(self, event):
            if event.type() == QEvent.Type.User + 1:
                event.fn()
                return True
            return False

    class ReenterQtEvent(QEvent):
        """ This is the QEvent that will be handled by the ReenterQtObject.
            self.fn is the next entry point of the asyncio event loop. """
        def __init__(self, fn):
            super().__init__(QEvent.Type(QEvent.Type.User + 1))
            self.fn = fn

    __loop = asyncio.new_event_loop()
    asyncio.set_event_loop(__loop)
    __tasksCounter = 0
    __lock = Lock()

    def __init__(self):
        super().__init__()
        self.reenterQt = self.ReenterQtObject()

    def addWorker(self, worker):
        worker.connect(self.__onTaskDone)

    def addTask(self, task, *args):
        """ To use asyncio and Qt together, one must run the asyncio
            event loop as a "guest" inside the Qt "host" event loop. """
        with self.__lock:
            self.__tasksCounter += 1
        self.__loop.create_task(task(*args))
        self.__loop.call_soon(self.__nextRunSchedule)
        self.__loop.run_forever()

    @Slot()
    def __onTaskDone(self):
        """ When all our current asyncio tasks are finished, we must end
            the "guest run" lest we enter a quasi idle loop of switching
            back and forth between the asyncio and Qt loops. We can
            launch a new guest run by calling launch_guest_run() again. """
        with self.__lock:
            self.__tasksCounter -= 1

    def __continueLoop(self):
        """ This function is called by an event posted to the Qt event
            loop to continue the asyncio event loop. """
        if self.__tasksCounter > 0:
            self.__loop.call_soon(self.__nextRunSchedule)
            self.__loop.run_forever()

    def __nextRunSchedule(self):
        """ This function serves to pause and re-schedule the guest
            (asyncio) event loop inside the host (Qt) event loop. It is
            registered in asyncio as a callback to be called at the next
            iteration of the event loop. When this function runs, it
            first stops the asyncio event loop, then by posting an event
            on the Qt event loop, it both relinquishes to Qt's event
            loop and also schedules the asyncio event loop to run again.
            Upon handling this event, a function will be called that
            resumes the asyncio event loop. """
        self.__loop.stop()
        QApplication.postEvent(self.reenterQt, self.ReenterQtEvent(self.__continueLoop))

Helper = AsyncHelper()