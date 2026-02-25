import json
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 8000
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str

    API_KEY_ABSTRACT_API: str
    X_MASTER_KEY: str
    X_ACCESS_KEY: str
    TG_BOT_TOKEN: str
    TG_CHAT_ID: str

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_BUCKET: str
    AWS_ENDPOINT_URL: str

    LOG_LEVEL: str = "INFO"
    LOG_RETENTION_DAYS: int = 7
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    LOG_FILE_PREFIX: str = "tasktaskgo"

    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/settings/.env')

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    def load_logging_config(self):
        """Загрузка настроек логирования из JSON файла"""
        config_file = os.path.join(self.BASE_DIR, 'settings', 'settings.json')
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.LOG_RETENTION_DAYS = config.get('log_retention_days', 7)
                self.LOG_FORMAT = config.get('log_format', self.LOG_FORMAT)
                self.LOG_FILE_PREFIX = config.get('log_file_prefix', 'tasktaskgo')
                self.LOG_LEVEL = config.get('log_level', 'INFO')
        except FileNotFoundError:
            # Используем значения по умолчанию
            pass


settings = Settings()
settings.load_logging_config()