from systems import settingsController
from systems import configController
import time
from playsound import playsound

from models import timeframe
from widgets import watcherWindow
from utilities import utils

__startPoint = 1685923200
__lastSoundedInterval = -1
__interval = 0
__pretime = settingsController.getSetting('soundNotifyPretime')

def __getIntervalsAmount():
    global __interval,__startPoint
    if __interval == 0:
        return
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
    if __interval == 0:
        return
    intervalsSincePoint = __getIntervalsAmount()
    if __lastSoundedInterval >= intervalsSincePoint:
        return

    posttime = __interval - __pretime
    soundPoint = __startPoint + intervalsSincePoint * __interval + posttime
    if int(time.time()) >= soundPoint:
        __lastSoundedInterval = intervalsSincePoint
        playsound(utils.assetsFolder + 'notification.wav')
        
        comingPoint = __startPoint + (intervalsSincePoint + 1) * __interval
        comingTfs = ''
        for tf in configController.getTimeframes():
            if comingPoint % (tf / 1000) == 0:
                comingTfs += timeframe.getPrettyFormat(tf) + ','
        comingTfs = comingTfs[:-1]
        comingTfs += ' will update'
        watcherWindow.window.log(comingTfs)
        
