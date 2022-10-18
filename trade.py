#!/usr/bin/python0.5
# -*- coding: iso-8859-1 -*
""" Python starter bot for the Crypto Trader games, from ex-Riddles.io """
__version__ = "1.0"

def nums(first_number, last_number, step=1):
    return range(first_number, last_number+1, step)

def stdev(data, count):

    mean = 0
    var = 0
    res = 0
    mean = sum([data[i] for i in nums(count - 50, count)]) / 50
    var = sum([((data[i] - mean) ** 2) for i in nums(count - 50, count)]) / 50
    res = var ** 0.5
    return res

def stdDevBis(data):
    mean = 0
    mean = sum(data) / len(data)
    variance = sum([((x - mean) ** 2) for x in data]) / len(data)
    stddev = variance ** 0.5
    return stddev


def _sma7(data,y):
    sma7 = 0
    for i in nums(y - 11, y):
        sma7 = sma7 + data[i - 1]
    sma7 = sma7 / 12
    return float(sma7)

def _sma24(data, y):
    sma24 = 0
    for i in nums(y - 23, y):
        sma24 = sma24 + data[i - 1]
    sma24 = sma24 / 24
    return float(sma24)

def _RSI(data, y):
    aVgUp = 0
    aVgDown = 0
    tmp = 0
    countUp = 0
    countDown = 0
    RS = 0

    for i in nums(y - 14, y-1):
        tmp = data[i] - data[i - 1]
        if (tmp > 0):
            aVgUp += tmp
            countUp += 1
            tmp = 0
        else:
            aVgDown += tmp
            countDown += 1
            tmp = 0        
    RS = ((aVgUp / countUp) / (aVgDown * -1 / countDown))
    return (100 - (100 / (1 + RS)))

def _signal9(data, y):
    signal9 = 0
    for i in nums(y - 8, y):
        signal9 = signal9 + data[i - 1]
    signal9 = signal9 / 8
    return float(signal9)


class Bot:

    def __init__(self):
        self.botState = BotState()
        self.i = 0
        self.y = 0
        self.z = 0
        self.liste = []
        self.sdCP = 0
        self.mSD = 0
        self.sma7 = []
        self.sma24 = []
        self.MACD = []
        self.signal = []
        self.RSI = []
        self.check = 0
        self.myValue = 0

    def run(self):
        while True:
            reading = input()
            if len(reading) == 0:
                continue
            self.parse(reading)




    def parse(self, info: str):
        tmp = info.split(" ")
        if tmp[0] == "settings":
            self.botState.update_settings(tmp[1], tmp[2])
        if tmp[0] == "update":
            if tmp[1] == "game":
                self.botState.update_game(tmp[2], tmp[3])
                if tmp[2] == "next_candles":
                    self.y += 1
        if tmp[0] == "action":
            if (self.i == 0):
                liste = self.botState.charts["USDT_BTC"].closes
                if (_sma7(liste, self.y) > _sma24(liste, self.y)):
                    self.check = 1

            liste = self.botState.charts["USDT_BTC"].closes
            self.sma7.append(_sma7(liste, self.y))
            self.sma24.append(_sma24(liste, self.y))
            self.MACD.append(self.sma7[self.i] - self.sma24[self.i])
            self.RSI.append(_RSI(self.botState.charts["USDT_BTC"].closes, self.y))
            liste2 = self.MACD

            if (self.i > 8):
                self.signal.append(_signal9(liste2, self.i))
                self.z +=1

            current_closing_price = self.botState.charts["USDT_BTC"].closes[-1]
            dollars = self.botState.stacks["USDT"]
            affordable = dollars / current_closing_price

            if (self.i > 9):
                if (self.MACD[self.i - 1] < self.signal[self.z - 2]) and (self.MACD[self.i] > self.signal[self.z - 1]):
                    if (self.RSI[self.i] < 40  and affordable > 0):
                        print(f'buy USDT_BTC {affordable}', flush=True)
                    else:
                        print("no_moves", flush=True)
                elif (self.MACD[self.i - 1] > self.signal[self.z - 2]) and (self.MACD[self.i] < self.signal[self.z - 1]):
                    if (self.RSI[self.i] > 50 and self.botState.stacks["BTC"]):
                        print(f'sell USDT_BTC {self.botState.stacks["BTC"]}', flush=True)
                    else:
                        print("no_moves", flush=True)
                else:
                    print("no_moves", flush=True)
            else:
                print("no_moves", flush=True)
            self.i += 1

class Candle:
    def __init__(self, format, intel):
        tmp = intel.split(",")
        for (i, key) in enumerate(format):
            value = tmp[i]
            if key == "pair":
                self.pair = value
            if key == "date":
                self.date = int(value)
            if key == "high":
                self.high = float(value)
            if key == "low":
                self.low = float(value)
            if key == "open":
                self.open = float(value)
            if key == "close":
                self.close = float(value)
            if key == "volume":
                self.volume = float(value)

    def __repr__(self):
        return str(self.pair) + str(self.date) + str(self.close) + str(self.volume)


class Chart:
    def __init__(self):
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.indicators = {}

    def add_candle(self, candle: Candle):
        self.dates.append(candle.date)
        self.opens.append(candle.open)
        self.highs.append(candle.high)
        self.lows.append(candle.low)
        self.closes.append(candle.close)
        self.volumes.append(candle.volume)


class BotState:
    def __init__(self):
        self.timeBank = 0
        self.maxTimeBank = 0
        self.timePerMove = 1
        self.candleInterval = 1
        self.candleFormat = []
        self.candlesTotal = 0
        self.candlesGiven = 0
        self.initialStack = 0
        self.transactionFee = 0.1
        self.date = 0
        self.stacks = dict()
        self.charts = dict()

    def update_chart(self, pair: str, new_candle_str: str):
        if not (pair in self.charts):
            self.charts[pair] = Chart()
        new_candle_obj = Candle(self.candleFormat, new_candle_str)
        self.charts[pair].add_candle(new_candle_obj)

    def update_stack(self, key: str, value: float):
        self.stacks[key] = value

    def update_settings(self, key: str, value: str):
        if key == "timebank":
            self.maxTimeBank = int(value)
            self.timeBank = int(value)
        if key == "time_per_move":
            self.timePerMove = int(value)
        if key == "candle_interval":
            self.candleInterval = int(value)
        if key == "candle_format":
            self.candleFormat = value.split(",")
        if key == "candles_total":
            self.candlesTotal = int(value)
        if key == "candles_given":
            self.candlesGiven = int(value)
        if key == "initial_stack":
            self.initialStack = int(value)
        if key == "transaction_fee_percent":
            self.transactionFee = float(value)

    def update_game(self, key: str, value: str):
        if key == "next_candles":
            new_candles = value.split(";")
            self.date = int(new_candles[0].split(",")[1])
            for candle_str in new_candles:
                candle_infos = candle_str.strip().split(",")
                self.update_chart(candle_infos[0], candle_str)
        if key == "stacks":
            new_stacks = value.split(",")
            for stack_str in new_stacks:
                stack_infos = stack_str.strip().split(":")
                self.update_stack(stack_infos[0], float(stack_infos[1]))


if __name__ == "__main__":
    mybot = Bot()
    mybot.run()
