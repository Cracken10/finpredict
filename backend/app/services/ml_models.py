import pandas as pd
import numpy as np
import logging
from prophet import Prophet
from pmdarima import auto_arima
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)
MODELS: dict = {}

async def load_ml_models():
    """Ajusta ARIMA, Prophet y carga LSTM al iniciar la API."""
    try:
        # -- Histórico AAPL (descarga si falta) --
        try:
            df = pd.read_csv('data/AAPL_1y.csv', parse_dates=['Date'], index_col='Date')
        except FileNotFoundError:
            import yfinance as yf
            df = yf.Ticker('AAPL').history(period='1y')
            df.to_csv('data/AAPL_1y.csv')
        prices = df['Close'].values

        # -- ARIMA --
        logger.info("Ajustando ARIMA...")
        MODELS['arima'] = auto_arima(prices, seasonal=False, suppress_warnings=True)

        # -- Prophet --
        logger.info("Ajustando Prophet...")
        prophet_df = df.reset_index().rename(columns={'Date':'ds','Close':'y'})
        m = Prophet(); m.fit(prophet_df)
        MODELS['prophet'] = m

        # -- LSTM --
        logger.info("Cargando LSTM y Scaler...")
        scaler = MinMaxScaler().fit(prices.reshape(-1,1))
        lstm   = load_model('models/lstm_model.h5')
        MODELS['lstm_scaler'] = scaler
        MODELS['lstm']        = lstm

        logger.info("✅ Modelos ML listos.")
    except Exception as e:
        logger.error(f"Error cargando modelos ML: {e}")
        raise

def arima_infer(data: np.ndarray, steps: int) -> np.ndarray:
    return np.array(MODELS['arima'].predict(n_periods=steps))

def prophet_infer(df: pd.DataFrame, steps: int) -> np.ndarray:
    fut = MODELS['prophet'].make_future_dataframe(periods=steps)
    fc  = MODELS['prophet'].predict(fut)
    return fc['yhat'].tail(steps).values

def lstm_infer(data: np.ndarray, steps: int) -> np.ndarray:
    scaler = MODELS['lstm_scaler']
    arr_s  = scaler.transform(data.reshape(-1,1))
    seq    = arr_s[-1].reshape((1,1,1))
    model  = MODELS['lstm']
    preds  = []
    for _ in range(steps):
        p = model.predict(seq, verbose=0)[0][0]
        preds.append(p)
        seq = np.array([[p]]).reshape((1,1,1))
    return scaler.inverse_transform(np.array(preds).reshape(-1,1)).flatten()
