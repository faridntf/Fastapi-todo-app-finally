from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent

class Setting(BaseSettings):
    SQLALCHEMY_POSTGRES_DATABASE_URL: str
    
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_SECRET_KEY : str
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    
    SAMESITE_SETTING: str
    SECURE_SETTING : bool

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )

setting = Setting()
