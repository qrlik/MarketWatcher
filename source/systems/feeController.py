from systems import settingsController

__feePercent = settingsController.getSetting('acceptableFeePercent') / 2 # open + close order
__feePerShare = settingsController.getSetting('feePerShare')
__atrStrategyFactor = settingsController.getSetting('atrStrategyFactor')

def isFeeAcceptable(atr):
	global __feePerShare,__feePercent,__atrStrategyFactor
	if atr is None:
		return False
	
	atr = atr * __atrStrategyFactor
	minimumAtr = 100 * __feePerShare / __feePercent
	return atr >= minimumAtr
	