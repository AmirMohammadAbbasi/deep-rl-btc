from tensorflow.keras.models import load_model
from signal_generator import SignalGenerator
from preprocessing import preprocessing
from agent import Agent
import warnings
import yaml
import os

warnings.filterwarnings("ignore")

if __name__ == '__main__':
    with open(os.path.join('./config' + "/experiment_config.yml"), 'rb') as config_file:
        params = yaml.safe_load(config_file)
    phase = params['phase']
    initial_money = params['initial_money']
    window_size = params['window_size']
    iterations = params['iterations']
    create_data = params['create_data']
    voting_list = params['voting_list']
    name_data = params['name_data']
    if phase == 'train':
        if create_data:
            ftsp = SignalGenerator('./signal_generator/config', phase=phase)
        data = preprocessing(name_data=name_data, voting_list=voting_list)

        agent = Agent(window_size=window_size,
                      market_prices=data,
                      config_dirctory='./config')
        agent.train(iterations=iterations, initial_money=initial_money)
    else:
        if create_data:
            ftsp = SignalGenerator('./signal_generator/config', phase=phase)
        data = preprocessing(name_data=name_data, voting_list=voting_list)

        PATH = 'model/model.h5'

        agent = Agent(window_size=window_size,
                      market_prices=data,
                      config_dirctory='./config')
        model = load_model(PATH)
        agent.test(initial_money=initial_money, model=model, phase=phase)
