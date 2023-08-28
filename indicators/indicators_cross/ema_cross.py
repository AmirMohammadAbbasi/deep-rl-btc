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

def calc_ema():
    global df
    print(df.tail(2))
    print(df.shape)

    df['d_ema_10']=pta.ema(df[closeColumn], length = 10)
    df['d_ema_20']=pta.ema(df[closeColumn], length = 20)
    df['10_above_20'] = (df["d_ema_10"] >= df["d_ema_20"]).astype(int)
    df['ema_10_20'] = df['10_above_20'].diff().astype('Int64')
    print(df.head(5))


def plot_crossover():
    global df
    #plt.style.use('fivethirtyeight')
    plt.rcParams['figure.figsize'] = (15, 8)
    plt.grid()
    plt.ylabel("Price")
    plt.plot(df[closeColumn], label = 'BTC', color = 'k',alpha = 0.6)
    plt.plot(df['d_ema_10'], label = 'EMA 10',color = 'g')
    plt.plot(df['d_ema_20'], label = 'EMA 20',color = 'b')
    plt.plot(df[df["ema_10_20"] == 1].index, 
         df['d_ema_10'][df["ema_10_20"] == 1], 
         "^", markersize = 10, color = 'g', label = 'BUY')
    
    plt.plot(df[df["ema_10_20"] == -1].index, 
         df['d_ema_10'][df["ema_10_20"] == -1], 
         "v", markersize = 10, color = 'r', label = 'SELL')

    plt.title('BTC Moving Averages (10, 20)')
    plt.legend(loc = 'upper left')
    plt.show()
    


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
    df.drop('d_ema_10', inplace=True, axis=1)
    df.drop('d_ema_20', inplace=True, axis=1)
    df.drop('10_above_20', inplace=True, axis=1)
    df.to_csv(FILENAME)

def read_eod_data():
    global df
    try:
        df = pd.read_csv(FILENAME,parse_dates=[dateColumn])
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
    calc_ema()
    plot_crossover()
    save_csv(df)