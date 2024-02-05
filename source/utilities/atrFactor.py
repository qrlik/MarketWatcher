from enum import IntEnum
import utils

atrFactorToOrders = {}

class OrderType(IntEnum):
	LONG = 0
	SHORT = 1

class Order:
	def __init__(self, data):
		self.symbol = data['symbol']
		self.time = data['openTime']
		self.type = OrderType[data['type']]

		self.atrFactorToProfit = {}
		price = data['openPrice']
		atr = data['atr']
		for atrFactorStr, maxPrice in data['maxProfits'].items():
			atrFactor = float(atrFactorStr)
			change = maxPrice - price if self.type == OrderType.LONG else price - maxPrice
			assert(change >= 0.0)
			profitAtrFactor = change / (atr * atrFactor)
			self.atrFactorToProfit.setdefault(atrFactor, utils.floor(profitAtrFactor))

def addOrder(orderData):
	order = Order(orderData)
	for atrFactor, _ in order.atrFactorToProfit.items():
		atrFactorToOrders.setdefault(atrFactor, []).append(order)

def sortOrders():
	global atrFactorToOrders
	for factor, orders in atrFactorToOrders.items():
		orders.sort(reverse=True, key=lambda order: order.atrFactorToProfit.get(factor))

def calculateProfitFactor(list):
	for file in list:
		data = utils.loadJsonFile(utils.assetsFolder + 'deals/' + file)
		for orderData in data:
			addOrder(orderData)
	sortOrders()

	atrFactor = {}
	atrProfit = {}
	amounts = {}
	for factor, orders in atrFactorToOrders.items():
		index = 1
		amount = len(orders)
		atrFactor.setdefault(factor, -1.0)
		atrProfit.setdefault(factor, 0.0)
		amounts.setdefault(factor, (-1, -1))

		for order in orders:
			profitFactor = order.atrFactorToProfit.get(factor)
			if profitFactor < factor:
				break

			summaryProfit = profitFactor * index
			summaryLoss = amount - index
			summary = summaryProfit - summaryLoss
			if summary > atrProfit[factor]:
				atrFactor[factor] = profitFactor
				atrProfit[factor] = utils.floor(summary)
				amounts[factor] = (index, amount - index)
			index += 1

	print(str(atrFactor))
	print(str(atrProfit))
	print(str(amounts))

# {0.5: 2.56, 1.0: 1.18}
# {0.5: 15.48, 1.0: 5.979999999999999}

# {0.5: 2.56, 1.0: 1.18}
# {0.5: 21.28, 1.0: 6.599999999999998}

if __name__ == '__main__':
	calculateProfitFactor(['11_2023'])