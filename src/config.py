from __future__ import annotations
import logging
import os
import sys
from functools import lru_cache
from importlib import import_module
from pathlib import Path

try:
	_settings = import_module("pydantic_settings")
	BaseSettings = _settings.BaseSettings
	SettingsConfigDict = _settings.SettingsConfigDict
except ImportError:
	from pydantic import BaseSettings

	SettingsConfigDict = dict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",case_sensitive=False,extra="ignore")
    app_name: str = "market-dataplatform"
    app_env: str = "dev"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "market_data"
    postgres_user: str 
    postgres_password: str

    kafka_bootstrap_servers: str = "localhost:9092"
    s3_bucket_name: str 
    log_level: str = "INFO"

    @property
    def postgres_dsn(self) -> str:
        """
        Build the connection string from individual parts so callers never
        have to concatenate it themselves.
        """
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get the settings object. This is cached so that it is only created once.
    """
    return Settings()

def configure_logging(settings: Settings | None = None) -> None:
    """
    Call this once, as early as possible (e.g. in main.py or an Airflow DAG).
    After this, every logger in the project inherits the same format and level.
    """
    if settings is None:
        settings = get_settings()

    level = logging.getLevelName(settings.log_level.upper())

    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )