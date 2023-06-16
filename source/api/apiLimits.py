from utilities import utils

__current = 0
__limits = 1000 # 1200 in fact
__timestamp = 0
__interval = 60000
__maintenanceInterval = 120000
__limited = False

def parseRateLimits(data):
    global __limits,__interval
    if not isinstance(data, list):
        utils.logError('apiLimits:parseRateLimits wrong data type ' + str(data))
    for limit in data:
        if limit.get('rateLimitType', '') != 'REQUEST_WEIGHT':
            continue
        if limit.get('interval', '') != 'MINUTE':
            utils.logError('apiLimits:parseRateLimits unknown interval - ' + limit.get('interval', ''))
        else:
            __interval = __interval * limit.get('intervalNum', 1)
            __limits = limit.get('limit', __limits) * 0.8

def getLimits():
    return __limits

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
        __limited = True
        __timestamp = utils.getCurrentTime()



