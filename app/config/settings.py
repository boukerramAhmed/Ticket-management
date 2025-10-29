from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Gestion des Tickets"
    API_V1_STR: str = ""
    SQLALCHEMY_DATABASE_URL: str
    CORS_ORIGINS: list = ["*"]
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()
