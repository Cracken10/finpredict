import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
import yfinance as yf

from app.database import get_sql_db
from app.models.prediction_log import PredictionLog
from app.services.ml_models       import arima_infer, prophet_infer, lstm_infer
from app.services.chatgpt_service import fetch_chatgpt_response
from app.services.news_service    import get_news_for_ticker
from app.services.finbert_service import get_finbert_sentiment
from app.services.combine_service import combine_forecasts
from app.utils                    import parse_prompt
from app.routes.auth_routes       import get_current_user

router = APIRouter(prefix='/api', tags=['Predict'])

@router.post('/predict')
async def predict(
    prompt: str,
    user: str = Depends(get_current_user),
    db=Depends(get_sql_db)
):
    # 1) ticker y days
    ticker, days = parse_prompt(prompt)

    # 2) histórico (CSV o descarga)
    try:
        df = pd.read_csv(f'data/{ticker}_1y.csv', parse_dates=['Date'], index_col='Date')
    except FileNotFoundError:
        df = yf.Ticker(ticker).history(period='1y')
        df.to_csv(f'data/{ticker}_1y.csv')
    if df.empty:
        raise HTTPException(500, f"No hay datos históricos para {ticker}")

    # 3) ChatGPT
    cdata = await fetch_chatgpt_response(prompt)

    # 4) Noticias + FinBERT
    news = await get_news_for_ticker(ticker)
    f_s  = await get_finbert_sentiment(news, cdata['text'], ticker=ticker)

    # 5) ML inferencias
    ar = arima_infer(df['Close'].values, days)
    pr = prophet_infer(df, days)
    ls = lstm_infer(df['Close'].values, days)

    # 6) Combinar forecasts
    final    = combine_forecasts(cdata['forecast'], cdata['sentiment'], f_s, ar, pr, ls)
    direction= 'Subir' if final >= 0 else 'Bajar'

    # 7) Estructurar respuesta
    response = {
      'ticker': ticker,
      'days': days,
      'final_forecast': f"{final:.2f}%",
      'confidence': 0.75,
      'forecast_direction': direction,
      'no_news': len(news) == 0,
      'historical_data': {
        'dates': df.index.strftime('%Y-%m-%d').tolist(),
        'prices': df['Close'].tolist()
      },
      'forecast_data': {
        'dates': [
          (df.index[-1] + pd.Timedelta(days=i+1)).strftime('%Y-%m-%d')
          for i in range(days)
        ],
        'arima': ar.tolist(),
        'prophet': pr.tolist(),
        'lstm': ls.tolist()
      },
      'sources': ", ".join({n['source'] for n in news})
    }

    # 8) Guardar log en MariaDB
    log = PredictionLog(
      username=user,
      ticker=ticker,
      days=days,
      forecast_direction=direction,
      request_body={'prompt':prompt},
      response_body=response
    )
    db.add(log)
    await db.commit()
    return response

@router.get('/user/predict-history')
async def history(
    user: str = Depends(get_current_user),
    db=Depends(get_sql_db)
):
    """
    Devuelve los últimos 5 pronósticos para el dashboard.
    """
    result = await db.execute(
      select(PredictionLog)
        .filter_by(username=user)
        .order_by(PredictionLog.timestamp.desc())
        .limit(5)
    )
    logs = result.scalars().all()
    return [
      {
        'id':        l.id,
        'ticker':    l.ticker,
        'days':      l.days,
        'direction': l.forecast_direction,
        'timestamp': l.timestamp.isoformat()
      }
      for l in logs
    ]
