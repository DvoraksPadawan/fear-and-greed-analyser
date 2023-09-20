import requests
from datetime import datetime


class Day:
    price = -1
    fear_and_greed = -1
    def __init__(self, _timestamp):
        self.timestamp = _timestamp
        self.date = datetime.fromtimestamp(_timestamp)
    def set_price(self, _price):
        self.price = _price
    def set_fear_and_greed(self, _fear_and_greed):
        self.fear_and_greed = _fear_and_greed
    def __str__(self):
        date = "{0}.{1}.{2}".format(self.date.day, self.date.month, self.date.year)
        output = "\nDAY\n{0}\n{1}\n{2}\n{3}\n".format(date, self.timestamp, self.price, self.fear_and_greed)
        return output

class Position:
    def __init__(self, _timestamp, _date, _entry_fear_and_greed, _entry_usd_amount, _entry_btc_price, _long = True):
        self.timestamp = _timestamp
        self.date = _date
        self.entry_fear_and_greed = _entry_fear_and_greed
        self.entry_usd_amount = _entry_usd_amount
        self.entry_btc_price = _entry_btc_price
        self.btc_size = _entry_usd_amount/_entry_btc_price
        self.long = _long
    def update_values(self, _current_fear_and_greed, _current_btc_price):
        self.current_fear_and_greed = _current_fear_and_greed
        self.current_btc_price = _current_btc_price
        self.price_difference = _current_btc_price - self.entry_btc_price
        self.profit = self.price_difference * self.btc_size
        if not self.long:
            self.profit = - self.profit
        self.current_usd_value = self.entry_usd_amount + self.profit
        
    def __str__(self):
        date = "{0}.{1}.{2}".format(self.date.day, self.date.month, self.date.year)
        output = "\nPOSITION\n{0}\n{1}\nlong:{2}\nfear and greed:\n{3}\n{4}\nvalue in usd:\n{5}\n{6}\nbtc size:{7}\nbtc price:\n{8}\n{9}\nprice difference:{10}\nprice profit:{11}\n".format(
            date, 
            self.timestamp, 
            self.long, 
            self.entry_fear_and_greed, 
            self.current_fear_and_greed, 
            self.entry_usd_amount, 
            self.current_usd_value, 
            self.btc_size, 
            self.entry_btc_price, 
            self.current_btc_price, 
            self.price_difference, 
            self.profit)
        return output



class Analyser:
    days = []
    greeds = []
    fears = []
    multiplier = 1
    addend = 0
    multiplier2 = 1
    addend2 = 0
    positions = []
    opened_position = False
    long = True
    closing_long_line = 50
    closing_short_line = 50
    overall_profit = 0
    entry_amount = 1000
    unrealized_gains = 0
    def __init__(self, prices, fear_and_greeds, greed_lines, fear_lines):
        self.set_days(prices, fear_and_greeds)
        self.set_borderlines(greed_lines, fear_lines)
    def set_multipliers(self, _multiplier, _addend, _multiplier2 = 1, _addend2 = 0):
        self.multiplier = _multiplier
        self.addend = _addend
        self.multiplier2 = _multiplier2
        self.addend2 = _addend2
    def set_days(self, prices, fear_and_greeds):
        i = 0
        for daily_price in prices:
            day = Day(int(daily_price["time"])/1000)
            day.set_price(float(daily_price["priceUsd"]))
            if (day.timestamp == int(fear_and_greeds[i]["timestamp"])):
                day.set_fear_and_greed(int(fear_and_greeds[i]["value"]))
                i += 1
                self.days.append(day)
            #print(day)
    def set_borderlines(self, _greeds, _fears):
        _greeds.sort()
        _fears.sort(reverse = True)
        for greed in _greeds:
            self.greeds.append(greed)
        for fear in _fears:
            self.fears.append(fear)
    def watch_market(self):
        for day in self.days:
            print(day)
            if len(self.positions) > 0:
                self.update_positions(day)
            if self.opened_position == True:
                if (self.long) and (day.fear_and_greed >= self.closing_long_line):
                    self.close_positions()
                elif (not self.long) and (day.fear_and_greed <= self.closing_short_line):
                    self.close_positions()
            if (day.fear_and_greed < self.fears[0]):
                self.open_position(day, True)
            elif (day.fear_and_greed > self.greeds[0]):
                self.open_position(day, False)
            #input()
            
    def update_positions(self, day):
        self.unrealized_gains = 0
        for position in self.positions:
            position.update_values(day.fear_and_greed, day.price)
            print(position)
            self.unrealized_gains += position.profit
            # if (position.profit < - 0.5 * position.entry_usd_amount):
            #     self.close_position(position)
        print(self)
        
    
    def open_position(self, day, long):
        i = -1
        if long:
            for fear in self.fears:
                if day.fear_and_greed < fear:
                    i += 1
                else:
                    break
        else:
            for greed in self.greeds:
                if day.fear_and_greed > greed:
                    i += 1
                else:
                    break
        # i = 0
        # if long:
        #     for position in self.positions:
        #         i += 1
        # else:
        #     for position in self.positions:
        #         i += 1
        multiplier = self.multiplier ** i
        addend = self.addend * i
        entry_amount = (self.entry_amount * multiplier) + (addend * self.entry_amount)
        position = Position(day.timestamp, day.date, day.fear_and_greed, entry_amount, day.price, long)
        self.positions.append(position)
        #print(position)
        self.opened_position = True
        self.long = long
        print("OPENED!\n")


        
    def close_positions(self):
        self.overall_profit += self.unrealized_gains
        self.unrealized_gains = 0
        self.positions = []
        self.opened_position = False
        print("CLOSED!\n")
        print(self)
    def close_position(self, position):
        self.overall_profit += position.profit
        self.unrealized_gains -= position.profit
        self.positions.remove(position)
        if (len(self.positions) < 1):
            self.opened_position = False
        print("CLOSED POSITION!\n")
        print(self)

    def set_closing_lines(self, long, short):
        self.closing_long_line = long
        self.closing_short_line = short
    def set_entry_amount(self, _amount):
        self.entry_amount = _amount
    def __str__(self):
        return("unrealized gains:{0}\nrealized gains:{1}\noveral:{2}\n".format(self.unrealized_gains, self.overall_profit, self.overall_profit + self.unrealized_gains))







#start = 1502361589000
start = 1692966272000
start = 1676052688000
start = 1423591888000
start = 1672596688000
now = 1694346595000
URL = "https://api.coincap.io/v2/assets/bitcoin/history?interval=d1&start={0}&end={1}".format(start, now)
#URL = "https://api.coincap.io/v2/assets/bitcoin/history?interval=d1"
r = requests.get(url = URL)
data = r.json()
prices = data["data"]

URL = "https://api.alternative.me/fng/?limit=180"
r = requests.get(url = URL)
data = r.json()
fear_and_greeds = data["data"]
fear_and_greeds.reverse()

greed_lines = [60, 70, 80, 90]
fear_lines = [40, 30, 20, 10]
greed_lines = [70, 80, 90]
fear_lines = [30, 20, 10]
analyser = Analyser(prices, fear_and_greeds, greed_lines, fear_lines)
analyser.set_multipliers(1, 0)
analyser.set_closing_lines(60, 40)
analyser.set_entry_amount(1000)
analyser.watch_market()























print()
print()