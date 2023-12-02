import pandas_ta as pta
import pandas as pd
import datetime
import yaml
import tqdm
import os


class SignalGenerator:
    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
    directory = './data/'

    def __init__(self, config_dirctory, phase):
        with open(os.path.join(config_dirctory + "/signal_generator.yml"), 'rb') as config_file:
            self.params = yaml.safe_load(config_file)
        self.start_date = datetime.datetime.strptime(self.params['start_date'], self.datetime_format)
        self.end_date = datetime.datetime.strptime(self.params['end_date'], self.datetime_format)
        self.market = self.params['market']
        self.time_frame = self.params['time_frame']
        self.phase = phase
        self.data = self.__clean_data()
        ''' Indicators '''
        # RSI
        self.rsi_length = self.params['rsi_length']
        self.rsi_upper_band = self.params['rsi_upper_band']
        self.rsi_lower_band = self.params['rsi_lower_band']
        self.__rsi()
        # MACD
        self.fast_length = self.params['fast_length']
        self.slow_length = self.params['slow_length']
        self.__macd()
        # Stoc
        self.k = self.params['k']
        self.d = self.params['d']
        self.smoth = self.params['smoth']
        self.stoch_upper_band = self.params['stoch_upper_band']
        self.stoch_lower_band = self.params['stoch_lower_band']
        self.__stoch()
        # ADX
        self.adx_length = self.params['adx_length']
        self.adx_thr = self.params['adx_thr']
        self.__adx()
        # EMA Cross
        self.ema_short_length = self.params['ema_short_length']
        self.ema_long_length = self.params['ema_long_length']
        self.__ema_cross()
        # Ichimoku
        self.tenkan = self.params['tenkan']
        self.kijun = self.params['kijun']
        self.__ichimoku()

    def __clean_data(self):
        data_path = './signal_generator/market_data_1m/' + self.market + '-1m.csv'
        data = pd.read_csv(data_path)
        data['datetime'] = pd.to_datetime(data['datetime'], format=self.datetime_format)
        data = data.drop_duplicates(subset="datetime", keep="first").set_index("datetime").sort_index()
        data['volume'].fillna(value=0, inplace=True)
        data['open'].fillna(method='ffill', inplace=True)
        data['high'].fillna(method='ffill', inplace=True)
        data['low'].fillna(method='ffill', inplace=True)
        data['close'].fillna(method='ffill', inplace=True)
        data = data.dropna()

        data = data[self.start_date: self.end_date]

        new_data = data.resample(self.time_frame).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'})
        new_data.drop(new_data.tail(1).index, inplace=True)

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        new_data.to_csv(os.path.join(self.directory,
                                     self.market + '-' + self.time_frame + '_' + self.phase + '.csv'), index=True)

        return new_data

    def __rsi(self):
        rsi_data = pd.DataFrame(columns=['RSI_' + str(self.rsi_length)],
                                data=pta.rsi(self.data[self.data.columns[3]],
                                             length=self.rsi_length).fillna(method='bfill'),
                                index=self.data.index)
        rsi_data['signal'] = 0
        for index, row in tqdm.tqdm(rsi_data.iterrows(), total=len(rsi_data)):
            if rsi_data.loc[index, rsi_data.columns[0]] < self.rsi_lower_band:
                rsi_data.loc[index, rsi_data.columns[1]] = 1
            elif rsi_data.loc[index, rsi_data.columns[0]] > self.rsi_upper_band:
                rsi_data.loc[index, rsi_data.columns[1]] = -1

        rsi_data.to_csv(os.path.join(self.directory, 'rsi_signals_' + self.phase + '.csv'), index=True)

    def __macd(self):
        macd_data = pta.macd(self.data[self.data.columns[3]],
                             fast=self.fast_length,
                             slow=self.slow_length).fillna(method='bfill')
        macd_data['signal'] = 0
        pre_index = []
        for index, row in tqdm.tqdm(macd_data.iterrows(), total=len(macd_data)):
            if macd_data.index.get_loc(index) != 0:
                if ((macd_data.loc[index, macd_data.columns[0]] > macd_data.loc[index, macd_data.columns[2]]) and
                        (macd_data.loc[index, macd_data.columns[1]] >= macd_data.loc[pre_index, macd_data.columns[1]])):
                    macd_data.loc[index, macd_data.columns[3]] = 1
                elif macd_data.loc[index, macd_data.columns[0]] <= macd_data.loc[index, macd_data.columns[2]]:
                    macd_data.loc[index, macd_data.columns[3]] = -1
            pre_index = index
        macd_data.to_csv(os.path.join(self.directory, 'macd_signals_' + self.phase + '.csv'), index=True)

    def __stoch(self):
        stoch_data = pta.stoch(self.data[self.data.columns[1]],
                               self.data[self.data.columns[2]],
                               self.data[self.data.columns[3]],
                               k=self.k,
                               d=self.d,
                               smooth_k=self.smoth).fillna(method='bfill')
        stoch_data['signal'] = 0
        for index, row in tqdm.tqdm(stoch_data.iterrows(), total=len(stoch_data)):
            if ((stoch_data.loc[index, stoch_data.columns[0]] > stoch_data.loc[index, stoch_data.columns[1]]) and
                    (stoch_data.loc[index, stoch_data.columns[0]] < self.stoch_lower_band) and
                    (stoch_data.loc[index, stoch_data.columns[1]] < self.stoch_lower_band)):
                stoch_data.loc[index, stoch_data.columns[2]] = 1
            elif ((stoch_data.loc[index, stoch_data.columns[0]] < stoch_data.loc[index, stoch_data.columns[1]]) and
                    (stoch_data.loc[index, stoch_data.columns[0]] > self.stoch_upper_band) and
                    (stoch_data.loc[index, stoch_data.columns[1]] > self.stoch_upper_band)):
                stoch_data.loc[index, stoch_data.columns[2]] = -1
        stoch_data.to_csv(os.path.join(self.directory, 'stoch_signals_' + self.phase + '.csv'), index=True)

    def __adx(self):
        adx_data = pta.adx(self.data[self.data.columns[1]],
                           self.data[self.data.columns[2]],
                           self.data[self.data.columns[3]],
                           length=self.adx_length).fillna(method='bfill')
        adx_data['signal'] = 0
        for index, row in tqdm.tqdm(adx_data.iterrows(), total=len(adx_data)):
            if ((adx_data.loc[index, adx_data.columns[0]] >= self.adx_thr) and
                    (adx_data.loc[index, adx_data.columns[1]] > adx_data.loc[index, adx_data.columns[2]])):
                adx_data.loc[index, adx_data.columns[3]] = 1
            elif ((adx_data.loc[index, adx_data.columns[0]] >= self.adx_thr) and
                    (adx_data.loc[index, adx_data.columns[1]] < adx_data.loc[index, adx_data.columns[2]])):
                adx_data.loc[index, adx_data.columns[3]] = -1
        adx_data.to_csv(os.path.join(self.directory, 'adx_signals_' + self.phase + '.csv'), index=True)

    def __ema_cross(self):
        ema_data = pd.DataFrame(columns=['EMA_' + str(self.ema_short_length)],
                                data=pta.ema(self.data[self.data.columns[3]],
                                             length=self.ema_short_length).fillna(method='bfill'),
                                index=self.data.index)
        ema_data['EMA_' + str(self.ema_long_length)] = pta.ema(self.data[self.data.columns[3]],
                                                               length=self.ema_long_length).fillna(method='bfill')
        ema_data['signal'] = 0
        for index, row in tqdm.tqdm(ema_data.iterrows(), total=len(ema_data)):
            if ema_data.loc[index, ema_data.columns[0]] > ema_data.loc[index, ema_data.columns[1]]:
                ema_data.loc[index, ema_data.columns[2]] = 1
            elif ema_data.loc[index, ema_data.columns[0]] < ema_data.loc[index, ema_data.columns[1]]:
                ema_data.loc[index, ema_data.columns[2]] = -1
        ema_data.to_csv(os.path.join(self.directory, 'ema_cross_signals_' + self.phase + '.csv'), index=True)

    def __ichimoku(self):
        ichi_data = pta.ichimoku(self.data[self.data.columns[1]],
                                 self.data[self.data.columns[2]],
                                 self.data[self.data.columns[3]],
                                 tenkan=self.tenkan,
                                 kijun=self.kijun)[0].fillna(method='bfill')
        ichi_data = ichi_data.drop([ichi_data.columns[-1]], axis=1)

        ichi_data['signal'] = 0
        for index, row in tqdm.tqdm(ichi_data.iterrows(), total=len(ichi_data)):
            if ((ichi_data.loc[index, ichi_data.columns[2]] > ichi_data.loc[index, ichi_data.columns[3]]) and
                    (self.data.loc[index, self.data.columns[3]] > ichi_data.loc[index, ichi_data.columns[2]]) and
                    (self.data.loc[index, self.data.columns[3]] > ichi_data.loc[index, ichi_data.columns[3]]) and
                    (ichi_data.loc[index, ichi_data.columns[2]] > ichi_data.loc[index, ichi_data.columns[0]]) and
                    (ichi_data.loc[index, ichi_data.columns[2]] > ichi_data.loc[index, ichi_data.columns[1]]) and
                    (ichi_data.loc[index, ichi_data.columns[3]] > ichi_data.loc[index, ichi_data.columns[0]]) and
                    (ichi_data.loc[index, ichi_data.columns[3]] > ichi_data.loc[index, ichi_data.columns[1]])):
                ichi_data.loc[index, ichi_data.columns[4]] = 1
            elif ((ichi_data.loc[index, ichi_data.columns[2]] < ichi_data.loc[index, ichi_data.columns[3]]) and
                  (self.data.loc[index, self.data.columns[3]] < ichi_data.loc[index, ichi_data.columns[2]]) and
                  (self.data.loc[index, self.data.columns[3]] < ichi_data.loc[index, ichi_data.columns[3]]) and
                  (ichi_data.loc[index, ichi_data.columns[2]] < ichi_data.loc[index, ichi_data.columns[0]]) and
                  (ichi_data.loc[index, ichi_data.columns[2]] < ichi_data.loc[index, ichi_data.columns[1]]) and
                  (ichi_data.loc[index, ichi_data.columns[3]] < ichi_data.loc[index, ichi_data.columns[0]]) and
                  (ichi_data.loc[index, ichi_data.columns[3]] < ichi_data.loc[index, ichi_data.columns[1]])):
                ichi_data.loc[index, ichi_data.columns[4]] = -1
        ichi_data.to_csv(os.path.join(self.directory, 'ichimoku_signals_' + self.phase + '.csv'), index=True)



