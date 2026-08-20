import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str = "5432"
    DB_NAME: str

    APP_NAME: str = "Proyecto Final"
    DEBUG: bool = True

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str

    UPLOAD_DIR: str = os.path.join(os.getcwd(), "upload")
    STORAGE_STRATEGY: str

    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_DEFAULT_REGION: str = "us-east-2"

    AWS_S3_BUCKET_NAME: str | None = None

    # S3_DESTINATION_BUCKET: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # El settings solo deberia tener settings, mover la inicializacion del client
    # Debemos dejarlo en la clase encargada

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
