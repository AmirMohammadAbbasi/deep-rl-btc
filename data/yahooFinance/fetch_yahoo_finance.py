from datetime import date
import numpy as np
import pandas as pd

# Data Source
import yfinance as yf


from configparser import ConfigParser

# Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")

tickerInfo = config_object["TICKERINFO"]

tickers = tickerInfo['name']
period = tickerInfo['period']
interval = tickerInfo['interval']

start = tickerInfo['fromDate']
end = tickerInfo['toDate']

my_tickers = yf.Ticker(tickers)
historical = my_tickers.history(start=start, end=end, interval=interval)

# Get data
data = yf.download(tickers=tickers, start=start, end=end, interval=interval)
print(data)


# Returns the current local date
today = date.today()

DF = pd.DataFrame(data)

# save the dataframe as a csv file
path = "./history/{}-{}-{}--{}.csv".format(tickers, interval, start, end)
print(path)
DF.to_csv(path)
