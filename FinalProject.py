#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 22:36:57 2023

@author: thomashamm
"""


import pandas as pd
import numpy as np

class Cash5:
    def __init__(self):
        self._numbers_drawn = 0
        self._max_numbers = []
        self._dates = {}
    def set_ticketprice(self,price):
        try:
            self._price = float(price)
        except Exception as e:
            print(e)
    @property
    def ticket_price(self):
        return self._price
    def set_numbers_drawn(self, numbers_drawn):
        #
        try:
            self._numbers_drawn = int(numbers_drawn)
        except Exception as e:
            print(e)
    @property
    def numbers_drawn(self):
        return self._numbers_drawn
    def set_max_numbers(self,max_numbers):
        self._max_numbers = pd.DataFrame(max_numbers, columns=['date','num'])
        self._max_numbers['date'] = pd.to_datetime(self._max_numbers['date'], format='%m/%d/%Y')
        self._max_numbers = self._max_numbers.sort_values(by='date', ascending=False)
    @property
    def max_numbers(self):
        return self._max_numbers
    def add_drawings(self,drawings):
        self._cash5 = pd.read_csv(drawings)
        self._cash5 = self._cash5.iloc[0:-1]
        self._cash5['Date'] = pd.to_datetime(self._cash5['Date'], format='%m/%d/%Y')
        self._dates = {"Start": self._cash5['Date'].min(), "End": self._cash5['Date'].max()}
    def add_details(self,details):
        self._details = pd.read_csv(details)
        self._details['date'] = pd.to_datetime(self._details['date'], format='%m/%d/%Y')
    def drawings(self):
        return self._cash5.head()
    def get_drawings(self, start, end):
        return self._cash5.loc[self._cash5["Date"].between(start, end)]
    def get_details(self, start, end):
        return self._details.loc[self._details["date"].between(start, end)]
    @property
    def get_dates(self):
        return self._dates
    def set_prizes(self,prize_dict):
        self._prize_dict = prize_dict
    @property
    def prizes(self):
        return self._prize_dict

class Winnings:
    def __init__(self, lottery):
        self._numbers = []
        self._lottery = lottery
        #print(self._lottery.head())
        self._costs = 0
        self._winnings = 0
        self._plays = 0
        self._dates = self._lottery.get_dates
        self._prize_dict = self._lottery.prizes
        self._ROI = 0
        self._max_numbers = self._lottery.max_numbers
        
    def set_fixed_numbers(self,numbers):
        if len(numbers) == self._lottery.numbers_drawn:
            self._numbers = numbers
        else:
            print("Incorrect amount of numbers submitted")
    def set_dates(self,**kwargs):
        for key, value in kwargs:
            self._dates[key] = value
    @property
    def get_numbers(self):
        return self._numbers
    
    def _calculate_winnings(self, row):
        prize = 0
        matches = int(row['Matches'])
        dp = int(row['DP'])
        prize4 = "prize_4"
        prize5 = "prize_5"
        if dp == 1:
            prize4 = "prize_4_double_play"
            prize5 = "prize_5_double_play"
        if matches in self._prize_dict:
            prize = self._prize_dict[matches]
        elif matches == 4:
            temp = self._details.loc[self._details["date"] == row["Date"]]
            prize = temp.at[temp.index.values[0],prize4]
        elif matches == 5:
            temp = self._details.loc[self._details["date"] == row["Date"]]
            prize = temp.at[temp.index.values[0],prize5]
        return prize
    def _fixed_winnings(self):
        self._drawings = lottery.get_drawings(self._dates['Start'], self._dates['End']).copy()
        self._details = lottery.get_details(self._dates['Start'], self._dates['End']).copy()
        self._wins = self._drawings[self._drawings.loc[:,'Ball 1':'Ball 5'].isin(self._numbers)]
        self._drawings['Matches'] = self._wins.count(axis = 1)
        self._drawings['Prizes_Won'] = self._drawings.apply(lambda row: self._calculate_winnings(row), axis=1)
        return {"Plays": self._drawings.shape[0], "Winnings": self._drawings['Prizes_Won'].sum()}

    def _random_winnings(self):
        self._drawings = lottery.get_drawings(self._dates['Start'], self._dates['End']).copy()
        self._details = lottery.get_details(self._dates['Start'], self._dates['End']).copy()
        self._drawings["Matches"] = self._drawings.apply(lambda row: self._match_random(row), axis=1)
        self._drawings['Prizes_Won'] = self._drawings.apply(lambda row: self._calculate_winnings(row), axis=1)
        played = self._drawings.shape[0]
        won = self._drawings['Prizes_Won'].sum()
        return {"Plays": played, "Winnings": won}

    def get_ROI(self):
        if self._numbers != []:
            results = self._fixed_winnings()
        else:
            results = self._random_winnings()
        return int(results["Winnings"] - results["Plays"] * self._lottery.ticket_price)

    def _gen_random(self,date):
        if date >= self._max_numbers['date'].iloc[0]:
            max_number = self._max_numbers['num'].iloc[0]
        else:
            max_number = self._max_numbers.loc[self._max_numbers['date'] <= date]['num'].values[0]
        self._numbers = []
        for i in range(0, self._lottery.numbers_drawn):
            self._numbers.append(np.random.randint(1,max_number+1))
    def _match_random(self,row):
        self._gen_random(row["Date"])
        self._wins = row.loc['Ball 1':'Ball 5'].isin(self._numbers)
        return self._wins.sum()
    def random_fixed(self):
        self._numbers = []
        max_number = self._max_numbers['num'].iloc[-1]
        for i in range(0, self._lottery.numbers_drawn):
            self._numbers.append(np.random.randint(1,max_number+1))
         


lottery = Cash5()
lottery.set_ticketprice(1)
lottery.add_drawings("NCEL-Cash5.csv")
lottery.add_details("NCEL-Cash5-Detailed.csv")
lottery.set_numbers_drawn(5)
lottery.set_max_numbers([["10/27/2006",39],["05/15/2014",41],["11/04/2018",43]])
lottery.set_prizes({2:1,3:5})



fixed_numbers = Winnings(lottery)
fixed_numbers.set_fixed_numbers([5,8,14,32,37])
fresults = fixed_numbers.get_ROI()
print(fresults)
quick_numbers = Winnings(lottery)
qresults = quick_numbers.get_ROI()
print(qresults)


max_attempts = 150
fixed_attempts = []
qp_attempts = []

i = 0

while i < max_attempts:
    temp = Winnings(lottery)
    temp.random_fixed()
    fixed_attempts.append(temp.get_ROI())
    temp.get_ROI()
    temp = Winnings(lottery)
    qp_attempts.append(temp.get_ROI())
    i += 1
    #print(i)


results = pd.DataFrame({"Fixed Attempts":fixed_attempts,"QuickPick Attempts": qp_attempts})
print(results.describe())