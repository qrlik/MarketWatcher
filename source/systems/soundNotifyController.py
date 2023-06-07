from systems import settingsController
from systems import configController
import time
from playsound import playsound

__startPoint = 1685923200
__lastSoundedInterval = -1
__interval = 0
__pretime = settingsController.getSetting('soundNotifyPretime')

def __getIntervalsAmount():
    global __interval,__startPoint
    timeSincePoint = int(time.time()) - __startPoint
    return int(timeSincePoint / __interval)

def init():
    global __interval,__lastSoundedInterval
    __interval = int(configController.getTimeframes()[0] / 1000)

    __lastSoundedInterval = __getIntervalsAmount()
    posttime = __interval - __pretime
    soundPoint = __startPoint + __lastSoundedInterval * __interval + posttime
    if int(time.time()) < soundPoint:
        __lastSoundedInterval -= 1

def update():
    global __interval,__pretime,__startPoint,__lastSoundedInterval
    intervalsSincePoint = __getIntervalsAmount()
    if __lastSoundedInterval >= intervalsSincePoint:
        return

    posttime = __interval - __pretime
    soundPoint = __startPoint + intervalsSincePoint * __interval + posttime
    if int(time.time()) >= soundPoint:
        __lastSoundedInterval = intervalsSincePoint
        playsound('assets/notification.wav')
