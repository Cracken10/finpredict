import os
import yfinance as yf
import pandas as pd

def generate_data(ticker='AAPL'):
    os.makedirs('data', exist_ok=True)
    df = yf.Ticker(ticker).history(period='1y')
    if df.empty or len(df) < 100:
        raise ValueError(f"Datos insuficientes para {ticker}")
    df.to_csv(f'data/{ticker}_1y.csv')
    print(f"[+] data/{ticker}_1y.csv generado")

if __name__ == '__main__':
    generate_data()
