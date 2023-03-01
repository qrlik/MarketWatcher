from models import candle

class DeltaController:
    def getDelta(self):
        return self.__averageDelta

    def process(self, candle: candle.Candle):
        if len(self.__deltas) >= self.__size:
            self.__deltas.pop(0)
        denominator = candle.low if candle.close > candle.open else candle.high
        newDelta = abs(candle.high - candle.low) / denominator
        self.__deltas.append(newDelta)
        self.__averageDelta = sum(self.__deltas) / len(self.__deltas)
        
    __deltas = []
    __averageDelta = 0.0
    __size = 25
