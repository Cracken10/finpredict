import json
from fastapi import HTTPException
from newsapi import NewsApiClient
from tenacity import retry, stop_after_attempt, wait_fixed
from app.database import mongo_db, redis_client
from app.config import settings

newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
async def get_news_for_ticker(ticker: str) -> list[dict]:
    """
    1) Leer cache Redis (1h)
    2) Si no, llamar NewsAPI
    3) Guardar en MongoDB (bulk upsert)
    4) Cachear en Redis
    """
    key = f"news:{ticker}"
    if cached := await redis_client.get(key):
        return json.loads(cached)

    try:
        resp = newsapi.get_everything(q=ticker, language="en", page_size=20)
    except Exception as e:
        raise HTTPException(503, f"Error NewsAPI: {e}")

    articles = []
    for a in resp.get('articles', []):
        art = {
          'source':      a['source']['name'],
          'title':       a['title'],
          'description': a.get('description',''),
          'content':     a.get('content',''),
          'url':         a['url'],
          'date':        a['publishedAt']
        }
        articles.append(art)

    if articles:
        ops = [{
          'updateOne': {
            'filter': {'url': art['url']},
            'update': {'$set': art},
            'upsert': True
          }
        } for art in articles]
        await mongo_db.news.bulk_write(ops)

    await redis_client.setex(key, 3600, json.dumps(articles))
    return articles
