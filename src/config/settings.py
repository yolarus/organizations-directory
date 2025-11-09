import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_file = os.path.join(BASE_DIR, '.env')


class EnvSettings(BaseSettings):
    """Env Settings."""
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding='utf-8',
        extra='ignore'
    )


class AppSettings(EnvSettings):
    """App settings."""
    DEBUG: bool = False
    STATIC_TOKEN: str = ''


class DatabaseSettings(EnvSettings):
    """Database Settings."""
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_NAME: str
    DB_PASSWORD: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._database_url = None

    @property
    def database_url(self):
        """URL database Postgres."""
        if self._database_url:
            return self._database_url
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @database_url.setter
    def database_url(self, value):
        """Setter of database url."""
        self._database_url = value

    @property
    def test_database_url(self):
        """URL test database."""
        return 'sqlite+aiosqlite:///:memory:'


class Config(EnvSettings):
    """Config."""
    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()


project_config = Config()
