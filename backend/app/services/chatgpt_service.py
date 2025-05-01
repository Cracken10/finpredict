import json
from fastapi import HTTPException
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_fixed
from app.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def fetch_chatgpt_response(prompt: str) -> dict:
    """
    Invoca GPT-4 function-calling para:
      - forecast  (número)
      - sentiment (número)
      - sources   (string)
    """
    resp = await client.chat.completions.create(
      model='gpt-4-1106-preview',
      messages=[{'role':'user','content':prompt}],
      functions=[{
        'name':'report_forecast',
        'parameters':{
          'type':'object',
          'properties':{
            'forecast': {'type':'number'},
            'sentiment':{'type':'number'},
            'sources':  {'type':'string'}
          },
          'required':['forecast','sentiment','sources']
        }
      }],
      function_call={'name':'report_forecast'},
      max_tokens=200
    )
    msg = resp.choices[0].message
    if msg.function_call:
        try:
            args = json.loads(msg.function_call.arguments)
            return {
                'forecast': float(args['forecast']),
                'sentiment':float(args['sentiment']),
                'sources':   args['sources'],
                'text':      msg.content or ''
            }
        except:
            raise HTTPException(502,'JSON inválido de OpenAI')
    return {'forecast':0.0,'sentiment':0.0,'sources':'','text':msg.content or ''}
