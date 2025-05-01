import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from app.database import redis_client
from typing import List, Dict

logger = logging.getLogger(__name__)

# Cargar FinBERT una sola vez
tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model     = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
model.eval()

async def get_finbert_sentiment(
    texts: List[Dict] | str,
    chatgpt_text: str = None,
    ticker: str = None
) -> float:
    """
    - texts: lista de noticias
    - chatgpt_text: resumen de ChatGPT
    - ticker: para cache Redis
    Devuelve score [-1.0, 1.0]
    """
    if ticker:
        cache_key = f"sentiment:{ticker}"
        if cached := await redis_client.get(cache_key):
            return float(cached)

    inputs = []
    if isinstance(texts, str):
        inputs.append(texts)
    else:
        inputs += [n.get('title','') for n in texts[:5] if n.get('title')]
        inputs += [n.get('description','') for n in texts[:5]]
    if chatgpt_text:
        inputs.append(chatgpt_text)

    if not inputs:
        return 0.0

    enc = tokenizer(
        inputs,
        padding=True,
        truncation=True,
        max_length=256,
        return_tensors="pt"
    )
    with torch.no_grad():
        out   = model(**enc)
        probs = torch.softmax(out.logits, dim=-1).numpy()

    scores = [p[0] - p[1] for p in probs]
    final  = float(sum(scores) / len(scores))

    if ticker:
        await redis_client.setex(cache_key, 3600, str(final))

    logger.info(f"FinBERT sentiment({ticker}): {final:.3f}")
    return round(final, 3)
