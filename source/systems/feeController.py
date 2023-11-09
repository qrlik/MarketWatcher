from systems import settingsController

__feePercent = settingsController.getSetting('acceptableFeePercent')
__feePerShare = settingsController.getSetting('feePerShare')

def isFeeAcceptable(atr):
	global __feePerShare,__feePercent
	if atr is None:
		return False
	
	feePercent = __feePerShare / atr * 100
	return feePercent <= __feePercent
	