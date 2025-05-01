import re
from fastapi import HTTPException
import yfinance as yf

def parse_prompt(prompt: str) -> tuple[str,int]:
    """
    1) Extrae ticker (1–5 letras)
    2) Extrae días (1–365)
    3) Valida existencia en yfinance
    """
    ticker_m = re.search(r"([A-Za-z]{1,5})", prompt)
    days_m   = re.search(r"(\d+)\s*d[ií]as?", prompt, re.IGNORECASE)

    ticker = ticker_m.group(1).upper() if ticker_m else "AAPL"
    days   = int(days_m.group(1))     if days_m   else 5

    if days < 1 or days > 365:
        raise HTTPException(400, "Días deben ser entre 1 y 365")

    info = yf.Ticker(ticker).info
    if not info or info.get("regularMarketPrice") is None:
        raise HTTPException(400, f"Ticker inválido: {ticker}")

    return ticker, days
