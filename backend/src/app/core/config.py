from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str 
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_EXPIRE_DAYS: int 
    HASH_KEY: str
    ROLE_SCOPE_MAP: dict 
    Database_url : str = "asijbg"
    host="localhost"
    port=6379
    tavily_api_key: str
    REDIS_CACHE_DB: int = 0
    REDIS_BROKER_DB: int = 1
    REDIS_RESULT_DB: int = 2
    decode_responses=True
    max_connections=100
    socket_connect_timeout=5
    socket_timeout=5 
    health_check_interval=30


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
        )

config_value = Settings() # type: ignore
