from utilities import utils

__cache = utils.loadJsonFile(utils.cacheFolder + 'cache')
__cache = __cache if __cache is not None else {}

def __save():
    utils.saveJsonFile(utils.cacheFolder + 'cache', __cache)

def __setField(key:str, value):
    __cache.setdefault(key, value)
    __save()

def __getField(key:str):
    return __cache.get(key)

def getLastConfigFilename():
    return __getField('lastConfigFilename')

def setLastConfigFilename(filename:str):
    return __setField('lastConfigFilename', filename)