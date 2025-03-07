from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import InputLayer, LSTM, Dense
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import RootMeanSquaredError
from tensorflow.keras.optimizers import Adam

def get_model(window_size, learning_rate=0.0001):
    model = Sequential()
    model.add(InputLayer((window_size, 14)))

    model.add(LSTM(64))
    model.add(Dense(32, 'relu'))

    model.add(Dense(8, 'linear'))

    model.compile(loss=MeanSquaredError(), optimizer=Adam(learning_rate=learning_rate), metrics=[RootMeanSquaredError()])

    return model

if __name__=='__main__':
    model = get_model(168)
    model.summary()