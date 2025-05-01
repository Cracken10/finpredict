import logging
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.security_headers import security_headers_middleware
from app.routes.auth_routes    import router as auth_router
from app.routes.predict_routes import router as pred_router
from app.services.ml_models    import load_ml_models, MODELS
from app.database import redis_client, get_sql_db, mongo_db

logging.basicConfig(level=logging.INFO)
app = FastAPI(title='FinPredict API')

# 1) Middleware: JWT blacklist + headers ligeros
app.middleware('http')(security_headers_middleware)

# 2) CORS: permite solo Nginx (http://localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# 3) Precarga de modelos ML al startup
@app.on_event('startup')
async def on_startup():
    await load_ml_models()

# 4) Rutas
app.include_router(auth_router)
app.include_router(pred_router)

# 5) Logging simple de cada petición
@app.middleware('http')
async def log_requests(request: Request, call_next):
    logging.info(f"{request.method} {request.url}")
    resp = await call_next(request)
    logging.info(f"Status: {resp.status_code}")
    return resp

# 6) Healthcheck completo
@app.get('/health')
async def health(db=Depends(get_sql_db)):
    try:
        # MariaDB
        await db.execute("SELECT 1")
        # Redis
        await redis_client.ping()
        # MongoDB
        await mongo_db.command("ping")
        # Modelos ML
        for key in ('arima','prophet','lstm','lstm_scaler'):
            if key not in MODELS:
                raise ValueError(f"Falta ML model: {key}")
        return {'status':'ok'}
    except Exception as e:
        logging.error(f"Healthcheck falló: {e}")
        raise HTTPException(503, "Servicio no disponible")
