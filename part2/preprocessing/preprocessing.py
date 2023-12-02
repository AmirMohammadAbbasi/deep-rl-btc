import pandas as pd


def preprocessing(name_data, voting_list):
    data = pd.read_csv('./data/' + name_data + '.csv')
    data.set_index(data.columns[0], inplace=True)
    data = data.drop([data.columns[4]], axis=1)
    for indicator in voting_list:
        data2 = pd.read_csv('./data/' + indicator + '.csv')
        data2.set_index(data2.columns[0], inplace=True)
        data[data2.columns[:-1]] = data2[data2.columns[:-1]]
    data = data.fillna(0)
    return data
