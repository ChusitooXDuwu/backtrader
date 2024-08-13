

import pandas as pd
import backtrader as bt
import matplotlib.pyplot as plt
plt.style.use("dark_background")
import mplfinance as mpf
import matplotlib.dates as dates
import datetime
import datetime as dt
import yfinance as yf
import numpy as np
import seaborn as sns
from datetime import datetime
import cufflinks as cf
from plotly.offline import iplot, init_notebook_mode
init_notebook_mode()
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"





ticker=['NVDA']
start = dt.datetime(2022,3,5)
end = dt.datetime.now()
df=yf.download(ticker, start, end)
print(df.head())
#df to txt sep
df.to_csv('NVDA.txt', header=True, index=True, sep=',', mode='w')