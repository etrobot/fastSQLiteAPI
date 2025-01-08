from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    db_path: str
    auth_token: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    settings = Settings()
    print(settings)  # 输出加载的设置
    return settings 