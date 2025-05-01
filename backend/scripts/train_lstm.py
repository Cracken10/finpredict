import os
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler

def train_lstm(ticker='AAPL'):
    os.makedirs('models', exist_ok=True)
    df = pd.read_csv(f'data/{ticker}_1y.csv', parse_dates=['Date'], index_col='Date')
    if df.empty or len(df) < 100:
        raise ValueError("Datos insuficientes para LSTM")
    prices = df['Close'].values.reshape(-1,1)

    scaler = MinMaxScaler().fit(prices)
    arr_s  = scaler.transform(prices)

    X, y = arr_s[:-1], arr_s[1:]
    X = X.reshape((X.shape[0],1,1))

    model = Sequential([LSTM(50, input_shape=(1,1)), Dense(1)])
    model.compile(optimizer='adam', loss='mse')
    es = EarlyStopping(patience=3, restore_best_weights=True)
    model.fit(X, y, epochs=50, validation_split=0.1, callbacks=[es], verbose=1)

    model.save('models/lstm_model.h5')
    print('[+] Modelo LSTM guardado en models/lstm_model.h5')

if __name__ == '__main__':
    train_lstm()
