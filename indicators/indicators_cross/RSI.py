from termcolor import colored as cl
from math import floor
import numpy as np
import requests
import pandas as pd
from pathlib import Path
import pandas_ta as pta
import traceback
import matplotlib.pyplot as plt

from configparser import ConfigParser

# Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")

tickerInfo = config_object["TICKERINFO"]
FILENAME = tickerInfo["path"]

df = None

closeColumn = 'Close'
dateColumn = 'Date'

RSI_Window = 14

rsi_signal = []


def calc_rsi():
    global df
    print(df.tail(2))
    print(df.shape)
    # print(list(df.columns.values))
    # print(df[closeColumn])

    df['rsi'] = pta.rsi(df[closeColumn], length=RSI_Window).fillna(50)
    print(df['rsi'])

    df['rsi_area'] = 0

    df['rsi_area'] = np.where(df['rsi'] > 70, -1, df['rsi_area'])
    df['rsi_area'] = np.where(df['rsi'] < 30 , 1, df['rsi_area'])

    rsi = df['rsi']
    prices = df[closeColumn]
    buy_price = []
    sell_price = []
    global rsi_signal
    signal = 0

    for i in range(len(rsi)):
        if (rsi[i-1] == 30 and rsi[i] == 30) or (rsi[i-1] == 70 and rsi[i] == 70):
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            rsi_signal.append(0)

        elif rsi[i-1] >= 30 and rsi[i] < 30:
            # if signal != 1:
            buy_price.append(prices[i])
            sell_price.append(np.nan)
            signal = 1
            rsi_signal.append(signal)
            # else:
            #     buy_price.append(np.nan)
            #     sell_price.append(np.nan)
            #     rsi_signal.append(0)
        elif rsi[i-1] < 70 and rsi[i] >= 70:
            # if signal != -1:
            buy_price.append(np.nan)
            sell_price.append(prices[i])
            signal = -1
            rsi_signal.append(signal)
            # else:
            #     buy_price.append(np.nan)
            #     sell_price.append(np.nan)
            #     rsi_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            rsi_signal.append(0)

    df['sell_price'] = sell_price
    df['buy_price'] = buy_price
    df['rsi_signal'] = rsi_signal

    print(df.tail(5))


def plot_crossover():
    global df
    plt.style.use('fivethirtyeight')
    plt.rcParams['figure.figsize'] = (20, 10)

    ax1 = plt.subplot2grid((10, 1), (0, 0), rowspan=4, colspan=1)
    ax2 = plt.subplot2grid((10, 1), (5, 0), rowspan=4, colspan=1)

    ax1.set_title('BTC CLOSE PRICE')
    ax2.set_title('BTC RELATIVE STRENGTH INDEX')

    ax1 = plt.subplot2grid((10, 1), (0, 0), rowspan=4, colspan=1)
    ax2 = plt.subplot2grid((10, 1), (5, 0), rowspan=4, colspan=1)
    ax1.plot(df[closeColumn], linewidth=2.5, color='skyblue', label='BTC')
    ax1.plot(df.index, df['buy_price'], marker='^', markersize=10,
             color='green', label='BUY SIGNAL')
    ax1.plot(df.index, df['sell_price'], marker='v',
             markersize=10, color='r', label='SELL SIGNAL')
    ax1.set_title('BTC RSI TRADE SIGNALS')
    ax2.plot(df['rsi'], color='orange', linewidth=2.5)
    ax2.axhline(30, linestyle='--', linewidth=1.5, color='grey')
    ax2.axhline(70, linestyle='--', linewidth=1.5, color='grey')
    plt.show()

    position = []
    global rsi_signal
    for i in range(len(rsi_signal)):
        if rsi_signal[i] > 1:
            position.append(0)
        else:
            position.append(1)

    for i in range(len(df[closeColumn])):
        if rsi_signal[i] == 1:
            position[i] = 1
        elif rsi_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]

    rsi = df['rsi']
    close_price = df[closeColumn]
    rsi_signal = pd.DataFrame(rsi_signal).rename(
        columns={0: 'rsi_signal'}).set_index(df.index)
    position = pd.DataFrame(position).rename(
        columns={0: 'rsi_position'}).set_index(df.index)


def check_file():
    try:
        filename = Path(FILENAME)
        if filename.is_file():
            return True
        else:
            print("File not found "+FILENAME)
            return False
    except Exception as e:
        print("Error reading data fromx CSV")
        print(e)
    return False


def save_csv(df):
    df.drop('buy_price', inplace=True, axis=1)
    df.drop('sell_price', inplace=True, axis=1)
    df.drop('rsi', inplace=True, axis=1)
    df.to_csv(FILENAME)


def read_eod_data():
    global df
    try:
        df = pd.read_csv(FILENAME, parse_dates=[dateColumn])
        df.set_index(dateColumn, inplace=True)
        print('finish read eod data')
        return True
    except Exception as e:
        print("Error reading data from CSV")
        print(e)
        print(traceback.format_exc())
        err_msg = "Internal error"
    return False


if __name__ == '__main__':
    if not check_file():
        print("File not found")
    if not read_eod_data():
        print("Error reading data")
    calc_rsi()
    plot_crossover()
    save_csv(df)
