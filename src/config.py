from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow", env_file_encoding="utf-8")

    # region postgresql
    PG_USERNAME: str
    PG_PASSWORD: str
    PG_HOST: str
    PG_PORT: int
    PG_DATABASE: str
    PG_POOL_SIZE: int
    # endregion

    # region other
    JWT_SECRET: str
    LOG_LOCATION: str
    DEBUG: bool
    # endregion


settings = _Settings()
