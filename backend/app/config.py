from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "Commerce Spell Checker"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str = "sqlite:///./data/spell_checker.db"
    
    CHROME_DRIVER_PATH: str = ""
    
    REPORT_OUTPUT_DIR: str = "./reports"
    LOG_DIR: str = "./logs"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
