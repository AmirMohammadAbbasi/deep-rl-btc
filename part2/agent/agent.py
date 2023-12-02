from models import LSTMNetwork, QTrainer
from collections import deque
import numpy as np
import warnings
import random
import tqdm
import os
import yaml
warnings.filterwarnings("ignore")


class Agent:
    def __init__(self,
                 window_size,
                 market_prices,
                 config_dirctory: str = './config'):
        self.window_size = window_size
        self.market_prices = market_prices
        self.features_size = len(self.market_prices.columns[4:])
        with open(os.path.join(config_dirctory + "/agent_config.yml"), 'rb') as config_file:
            self.params = yaml.safe_load(config_file)
        self.action_size = self.params['action_size']
        self.batch_size = self.params['batch_size']
        self.train_size = self.params['train_size']
        self.open_fee = self.params['open_fee']
        self.close_fee = self.params['close_fee']
        self.gamma = self.params['gamma']
        self.epsilon_greedy = self.params['epsilon_greedy']
        self.epsilon = self.params['epsilon']
        self.epsilon_max = self.params['epsilon_max']
        self.epsilon_min = self.params['epsilon_min']
        self.lr = self.params['lr']

        self.input_size = (self.features_size, window_size)
        self.memory = deque(maxlen=self.train_size)
        self.short_memory = deque(maxlen=self.batch_size)

        self.model = LSTMNetwork(self.input_size, self.action_size)
        self.model = self.model.create_model()
        self.trainer = QTrainer(self.model, lr=self.lr, gamma=self.gamma)

    def act(self, state, epsilon=None, phase: str = 'train'):
        if phase == 'train':
            if random.random() <= epsilon:
                return random.randrange(self.action_size)
            else:
                prediction = self.model(np.reshape(state, [1, state.shape[0], state.shape[1]]))
                return np.argmax(prediction)
        else:
            prediction = self.model(np.reshape(state, [1, state.shape[0], state.shape[1]]))
            return np.argmax(prediction)

    def get_state(self, t):
        state = np.array([])
        for counter in np.arange(0, self.window_size):
            indicators = self.market_prices[self.market_prices.columns[4:]].iloc[1].values
            if counter == 0:
                state = np.zeros((indicators.shape[0], 1))
            state = np.column_stack((state, indicators.reshape(-1, 1)))
        return np.delete(state, [0], axis=1)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        states, actions, rewards, next_states, dones = zip(*self.memory)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self):
        states, actions, rewards, next_states, dones = zip(*self.short_memory)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train(self, iterations, initial_money):
        previous_profit = 0
        decay_factor = (self.epsilon_min / self.epsilon) ** (1 / iterations)
        epsilon = self.epsilon_max
        for i in tqdm.tqdm(np.arange(iterations)):
            epsilon = epsilon * decay_factor
            state = self.get_state(self.window_size)
            money = initial_money
            self.memory = deque(maxlen=self.train_size)
            self.short_memory = deque(maxlen=self.batch_size)
            for t in range(self.window_size, len(self.market_prices) - 1):
                action = self.act(state, epsilon, phase='train')
                next_state = self.get_state(t + 1)
                reward = float(0)
                if action == 1 and money > 0:
                    quantity = ((1 - self.open_fee) * money) / self.market_prices['close'].iloc[t]
                    next_day_money = 0
                    next_day_money += (self.__close_position(quantity,
                                                             self.market_prices['close'].iloc[t+1]))
                    profit = (next_day_money - money)/money * 100

                    money = next_day_money
                    reward = float(profit)
                elif action == 2 and money > 0:
                    quantity = ((1 - self.open_fee) * money) / self.market_prices['close'].iloc[t]
                    next_day_money = 0
                    next_day_money += (self.__close_position(quantity,
                                                             self.market_prices['close'].iloc[t + 1]))
                    profit = (next_day_money - money)/money * 100
                    money = next_day_money
                    reward = float(profit)
                if random.random() <= (self.train_size/len(self.market_prices)):
                    self.remember(state, action, reward, next_state,
                                  t >= len(self.market_prices) - 1)
                self.short_memory.append((state, action, reward, next_state,
                                          t >= len(self.market_prices) - 1))

                state = next_state
                if (t + 1) % self.batch_size == 0:
                    self.train_short_memory()
            total_profit = money
            if total_profit > previous_profit:
                previous_profit = total_profit
                print('----->  epoch: %d,  ------>  total money: %f.3' % (i + 1, total_profit))
                self.model.save('./model/model.h5')
            self.train_long_memory()

    @staticmethod
    def __reward(profit):
        return float(profit)

    def test(self, initial_money, model, phase):
        self.model = model
        state = self.get_state(self.window_size)
        money = initial_money
        long_counter = 0
        short_counter = 0
        for t in range(self.window_size, len(self.market_prices) - 1):
            action = self.act(state, phase=phase)
            next_state = self.get_state(t + 1)
            if action == 1 and money > 0:
                quantity = ((1 - self.open_fee) * money) / self.market_prices['close'].iloc[t]
                next_day_money = 0
                next_day_money += (self.__close_position(quantity,
                                                         self.market_prices['close'].iloc[t + 1]))

                money = next_day_money
                long_counter += 1
            elif action == 2 and money > 0:
                quantity = ((1 - self.open_fee) * money) / self.market_prices['close'].iloc[t]
                next_day_money = 0
                next_day_money += (self.__close_position(quantity,
                                                         self.market_prices['close'].iloc[t + 1]))

                money = next_day_money
                short_counter += 1
            state = next_state

        print('profit: %f.3, initial money: %f, final_money: %f' % (((money - initial_money) / initial_money) * 100,
                                                                    initial_money,
                                                                    money))
        print('\nlong_count: %d, short_count: %d' % (long_counter, short_counter))

    def __close_position(self, quantity, price):
        return quantity * price - (1 - self.close_fee)
