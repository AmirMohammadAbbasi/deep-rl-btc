from termcolor import colored as cl
from math import floor
import numpy as np
import requests
import pandas as pd
from pathlib import Path
import pandas_ta as pta
import traceback
import matplotlib.pyplot as plt

FILENAME = "./BTC-USD-1d-period-2023-08-27.csv"
df = None

closeColumn = 'Close'
dateColumn = 'Date'

RSI_Window = 14


def calc_rsi():
    global df
    print(df.tail(2))
    print(df.shape)
    # print(list(df.columns.values))
    # print(df[closeColumn])

    df['rsi'] = pta.rsi(df[closeColumn], length=RSI_Window)

    rsi = df['rsi']
    prices = df[closeColumn]
    buy_price = []
    sell_price = []
    rsi_signal = []
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
    # ax1.plot(df[closeColumn], linewidth=2.5)
    ax1.set_title('BTC CLOSE PRICE')
    # ax2.plot(df['rsi'], color='orange', linewidth=2.5)
    # ax2.axhline(30, linestyle='--', linewidth=1.5, color='grey')
    # ax2.axhline(70, linestyle='--', linewidth=1.5, color='grey')
    ax2.set_title('BTC RELATIVE STRENGTH INDEX')
    # plt.show()

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

    # frames = [close_price, rsi, rsi_signal, position]
    # strategy = pd.concat(frames, join='inner', axis=1)

    # print(strategy.head())

    # BTC_ret = pd.DataFrame(np.diff(df[closeColumn])).rename(columns={0: 'returns'})
    # rsi_strategy_ret = []

    # for i in range(len(BTC_ret)):
    #     returns = BTC_ret['returns'][i]*strategy['rsi_position'][i]
    #     rsi_strategy_ret.append(returns)

    # rsi_strategy_ret_df = pd.DataFrame(
    #     rsi_strategy_ret).rename(columns={0: 'rsi_returns'})
    # investment_value = 100000
    # number_of_stocks = floor(investment_value/df[closeColumn][-1])
    # rsi_investment_ret = []

    # for i in range(len(rsi_strategy_ret_df['rsi_returns'])):
    #     returns = number_of_stocks*rsi_strategy_ret_df['rsi_returns'][i]
    #     rsi_investment_ret.append(returns)

    # rsi_investment_ret_df = pd.DataFrame(rsi_investment_ret).rename(
    #     columns={0: 'investment_returns'})
    # total_investment_ret = round(
    #     sum(rsi_investment_ret_df['investment_returns']), 2)
    # profit_percentage = floor((total_investment_ret/investment_value)*100)
    # print(cl('Profit gained from the RSI strategy by investing $100k in BTC : {}'.format(
    #     total_investment_ret), attrs=['bold']))
    # print(cl('Profit percentage of the RSI strategy : {}%'.format(
    #     profit_percentage), attrs=['bold']))


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
    # df.drop('d_ema_10', inplace=True, axis=1)
    # df.drop('d_ema_20', inplace=True, axis=1)
    # df.drop('10_above_20', inplace=True, axis=1)
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
    # save_csv(df)
