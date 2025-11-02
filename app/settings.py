from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRES_IN_MINUTES: int
    JWT_REFRESH_SECRET: str
    JWT_REFRESH_TOKEN_EXPIRES_IN_MINUTES: int
    TEST_DATABASE_URL: str
    N8N_BEARER_TOKEN: str | None = None
