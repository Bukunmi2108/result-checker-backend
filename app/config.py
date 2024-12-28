from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DOMAIN_URL: str

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = False

    SUPER_ADMIN_EMAIL: str
    SUPER_ADMIN_PASSWORD: str
    SUPER_ADMIN_FIRSTNAME: str
    SUPER_ADMIN_LASTNAME: str
    SUPER_ADMIN_PHONE_NUMBER: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()