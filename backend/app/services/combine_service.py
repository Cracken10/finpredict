def combine_forecasts(
    c_f: float,   # ChatGPT forecast
    c_s: float,   # ChatGPT sentiment
    f_s: float,   # FinBERT sentiment
    ar: list,     # ARIMA array
    pr: list,     # Prophet array
    ls: list      # LSTM array
) -> float:
    """
    Pesos fijos (ajustables):
      ChatGPT forecast 0.30
      ChatGPT senti    0.10
      FinBERT senti    0.10
      ARIMA            0.20
      Prophet          0.15
      LSTM             0.15
    """
    w = {'c_f':0.3,'c_s':0.1,'f_s':0.1,'a':0.2,'p':0.15,'l':0.15}
    return (
        c_f*w['c_f'] +
        c_s*w['c_s'] +
        f_s*w['f_s'] +
        float(ar[-1])*w['a'] +
        float(pr[-1])*w['p'] +
        float(ls[-1])*w['l']
    )
