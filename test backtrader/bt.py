from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

import pandas as pd
import backtrader as bt
import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib.dates as dates
import datetime

import yfinance as yf
import numpy as np
import seaborn as sns

import cufflinks as cf
# from plotly.offline import iplot, init_notebook_mode
# init_notebook_mode()
# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = "all"


#Pedir el Ticker a usar y las fecha de inicio y fin

ticker = (input("Ingrese el Ticker a usar: "))
start_year = int(input("Ingrese el año de inicio (yyyy): "))
start_month = int(input("Ingrese el mes de inicio (mm): "))
start_day = int(input("Ingrese el dia de inicio (dd): "))
end_year = int(input("Ingrese el año de fin (yyyy): "))
end_month = int(input("Ingrese el mes de fin (mm): "))
end_day = int(input("Ingrese el dia de fin (dd): "))


ticker=[ticker]
df=yf.download(ticker)

#df to txt sep
df.to_csv(ticker[0] + '.txt', header=True, index=True, sep=',', mode='w')

def calculate_volatility(data, period = 14):
    returns = data['close'].pct_change()
    volatility = returns.rolling(window=period).std()
    return volatility




class SMA_Strategy_2(bt.Strategy):
    params = (
        ('maperiod_200', 200),
        ('maperiod_5', 5),
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Indicators
        self.sma_200 = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod_200)
        self.sma_5 = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod_5)
        # calcualte winrate
        self.winrate = 0
        self.win = 0
        self.loss = 0

        self.position_open = False
        self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                self.entry_price = order.executed.price
            else:
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                #calculate winrate
                if order.executed.price > self.entry_price:
                    self.win += 1
                else:
                    self.loss += 1

                    self.winrate = self.win / (self.win + self.loss)
                self.log(f'Winrate: {self.winrate:.2f}')
                #print amount of trades
                self.log(f'Amount of trades: {self.win + self.loss}')
            self.bar_executed = len(self)
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None   

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}')

    def next(self):
        if self.order:
            return

        if not self.position:
            # Check if the conditions for buying are met
            if self.dataclose[0] > self.sma_200[0]:
                if (self.dataclose[0] < self.dataopen[0] and  # Day 1: Red candle
                    self.dataclose[-1] < self.dataopen[-1] and  # Day 1: Red candle
                    self.dataclose[-2] < self.dataopen[-2] and  # Day 2: Red candle
                    self.dataclose[0] < self.dataclose[-1] and  # Day 1: Open < Previous Close
                    self.dataclose[-1] < self.dataclose[-2] and  # Day 1: Open < Previous Close
                    self.dataclose[-2] < self.dataclose[-3]):  # Day 2: Open < Previous Close
                        # Day 3: Open < Previous Close
                    
                    self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')
                    self.order = self.buy()

        else:
            # Check if the conditions for selling are met
            if self.dataclose[0] > self.sma_5[0]:
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')
                self.order = self.sell()



                
        

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(SMA_Strategy_2)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, ticker[0] + '.txt')

    # Create a Data Feed
    data = bt.feeds.YahooFinanceData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(start_year, start_month, start_day),
        # Do not pass values before this date
        todate=datetime.datetime(end_year, end_month, end_day),
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.00)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    #add in the plot the winrate
    

    # Plot the result
    #agrega literalmente el winrate dentro del grafico
    
    
    cerebro.plot(style='candlestick')