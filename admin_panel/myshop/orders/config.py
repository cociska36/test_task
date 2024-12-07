from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env

class Settings(BaseSettings):
    bot_token: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    channel_id: str
    group_id: str

    class Config:
        env_file = ".env"

# Создаем объект конфигурации
settings = Settings()
