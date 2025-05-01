import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # MariaDB
    MYSQL_HOST:     str = os.getenv('MYSQL_HOST')
    MYSQL_PORT:     str = os.getenv('MYSQL_PORT')
    MYSQL_USER:     str = open(os.environ['MYSQL_USER_FILE']).read().strip()
    MYSQL_PASSWORD: str = open(os.environ['MYSQL_PASSWORD_FILE']).read().strip()
    MYSQL_DATABASE: str = open(os.environ['MYSQL_DATABASE_FILE']).read().strip()

    # MongoDB
    MONGO_USERNAME: str = open(os.environ['MONGO_USERNAME_FILE']).read().strip()
    MONGO_PASSWORD: str = open(os.environ['MONGO_PASSWORD_FILE']).read().strip()

    # APIs externas
    OPENAI_API_KEY: str = open(os.environ['OPENAI_API_KEY_FILE']).read().strip()
    NEWS_API_KEY:    str = open(os.environ['NEWS_API_KEY_FILE']).read().strip()

    # JWT
    SECRET_KEY:         str = open(os.environ['SECRET_KEY_FILE']).read().strip()
    REFRESH_SECRET_KEY: str = open(os.environ['REFRESH_SECRET_KEY_FILE']).read().strip()

    # Otros
    FRONTEND_URL: str
    REDIS_URL:    str

    @property
    def MARIADB_URL(self) -> str:
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:"
            f"{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:"
            f"{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    @property
    def MONGODB_URL(self) -> str:
        return (
            f"mongodb://{self.MONGO_USERNAME}:"
            f"{self.MONGO_PASSWORD}@mongo:27017/"
            "finpredict?authSource=admin"
        )

    class Config:
        case_sensitive = True

settings = Settings()
