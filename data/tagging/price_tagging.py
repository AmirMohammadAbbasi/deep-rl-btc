import pandas as pd
from pathlib import Path
import traceback

from configparser import ConfigParser

# Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")

tickerInfo = config_object["TICKERINFO"]
FILENAME = tickerInfo["path"]

df = None

closeColumn = 'Close'
dateColumn = 'Date'


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
    # df.drop('d_sma_10', inplace=True, axis=1)
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





def tagging():
    global df
    print(df.tail(2))
    print(df.shape)


    df['10_above_20'] = (df["d_sma_10"] >= df["d_sma_20"]).astype(int)
    df['sma_10_20'] = df['10_above_20'].diff().astype('Int64')
    print(df.tail(5))



if __name__ == '__main__':
    if not check_file():
        print("File not found")
    if not read_eod_data():
        print("Error reading data")
    save_csv(df)