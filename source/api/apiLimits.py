from utilities import utils

__current = 0
__limits = 800 # 1200 in fact
__timestamp = 0
__interval = 60000
__maintenanceInterval = 120000
__limited = False

def getAllowedAmount():
    return max(__limits - __current, 0)

def isAllowed():
    global __timestamp,__interval,__current,__limited
    if utils.getCurrentTime() > __timestamp + __interval:
        __current = 0
        __limited = False
    return __limited or __current < __limits

def onMaintenance():
    global __maintenanceInterval,__timestamp,__current,__interval,__limited
    __timestamp = utils.getCurrentTime() + __maintenanceInterval + __interval
    __limited = True
    __current = __limits

def onError(message:str):
    global __current,__limits,__timestamp,__limited
    if __limited:
        return
    __limited = True
    __current = __limits
    bannedUntil = 'unknown'
    firstSplit = message.split('IP banned until ')
    if len(firstSplit) > 1:
        bannedUntil = firstSplit[1].split('. Please use')[0]
    if bannedUntil.isdigit():
        bannedUntil = int(bannedUntil) + 1000
        __timestamp = bannedUntil
        waitFor = int((__timestamp + __interval - utils.getCurrentTime()) / 1000)
        utils.log('Banned for ' + str(waitFor) + ' sec')
    else:
        __timestamp = utils.getCurrentTime()
        waitFor = int((__timestamp + __interval - utils.getCurrentTime()) / 1000)
        utils.log('Limited for ' + str(waitFor) + ' sec')

def onResponce(result):
    global __timestamp,__current,__limited
    weight = result.get('x-mbx-used-weight-1m', None)
    if not weight:
        utils.logError('apiLimits:onResponce no weight - ' + str(result))
    __current = max(__current, int(weight))
    if __current >= __limits and not __limited:
        utils.log('Paused for ' + str(__interval / 1000) + ' sec')
        __limited = True
        __timestamp = utils.getCurrentTime()



