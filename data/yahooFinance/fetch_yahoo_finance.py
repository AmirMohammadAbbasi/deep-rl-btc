import numpy as np
import pandas as pd

# Data Source
import yfinance as yf

tickers = 'BTC-USD'
# period = '1mo'
interval = '1d'

start="2019-06-02"
end="2021-06-10"

my_tickers= yf.Ticker(tickers)
historical = my_tickers.history(start=start, end=end, interval=interval)


# Get data
data = yf.download(tickers=tickers, start=start, end=end, interval=interval)
print(data)

from datetime import date
 
# Returns the current local date
today = date.today()

DF = pd.DataFrame(data)
 
# save the dataframe as a csv file
path = "history/{}-{}-{}-{}.csv".format(tickers, interval, "period", today)
print(path)
DF.to_csv(path)