from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    session_dispose_sec: float
    imgur_client_id: str
    imgur_client_secret: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
