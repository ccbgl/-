from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AutoTest Platform"
    DATABASE_URL: str# 数据库连接字符串
    REDIS_URL: str  # Redis 连接字符串
    SECRET_KEY: str # JWT 密钥
    ACCESS_TOKEN_EXPIRE_MINUTES: int   # JWT 过期时间
    REPO_URL: str
    # .env
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()