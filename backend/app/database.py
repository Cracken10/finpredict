from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import redis.asyncio as aioredis
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# --- MariaDB (SQLAlchemy async) ---
engine = create_async_engine(settings.MARIADB_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_sql_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- Redis (cache & JWT blacklist) ---
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

# --- MongoDB (Motor) para noticias ---
mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
mongo_db     = mongo_client.get_default_database()
