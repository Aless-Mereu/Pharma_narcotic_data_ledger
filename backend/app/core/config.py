from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pharma Narcotics Ledger GxP"
    DATABASE_URL: str = "postgresql+asyncpg://gxp_admin:gxp_secure_password_2026@db:5432/pharma_narcotics_db"
    SECRET_KEY: str = "gxp_jwt_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True

settings = Settings()