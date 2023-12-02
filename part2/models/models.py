import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
import warnings

warnings.filterwarnings("ignore")


class LSTMNetwork:
    def __init__(self, input_size, output_size):
        super().__init__()
        self.input_size = input_size
        self.output_size = output_size

    def create_model(self):
        model = Sequential()
        model.add(LSTM(50, input_shape=self.input_size))
        model.add(Dense(self.output_size))
        model.compile(optimizer='adam',
                      loss=tf.keras.losses.MeanSquaredError())
        return model


class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model

    def train_step(self, state, action, reward, next_state, done):
        state = np.asarray(state)
        next_state = np.asarray(next_state)
        action = np.asarray(action)
        reward = np.asarray(reward)

        pred = self.model.predict(state, verbose=0)
        pred_act_next_state = self.model.predict(next_state, verbose=0)

        target = np.copy(pred)
        for idx in range(len(done)):
            q_new = reward[idx]
            if not done[idx]:
                q_new = reward[idx] + self.gamma * np.max(pred_act_next_state[idx])
            target[idx][action[idx]] = q_new

        self.model.fit(state, target, batch_size=len(state), epochs=1, verbose=0)
