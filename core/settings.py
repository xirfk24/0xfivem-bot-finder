from enum import Enum
from pathlib import Path

from pydantic import (
    field_validator,
    ValidationInfo
)

from pydantic_settings import BaseSettings


class Env(str, Enum):

    DEV = 'dev'
    PROD = 'prod'


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    APP_ENV: Env

    DISCORD_TOKEN: str

    DATABASE_URL: str

    @field_validator("DATABASE_URL")
    def validate_database(cls, v: str, info: ValidationInfo):
        if isinstance(v, str) and v.startswith("sqlite"):
            return v
        raise ValueError("Invalid Database URL!")
    
    class Config:
        env_file = Path(__file__).parent.parent / ".env"


settings = Settings()