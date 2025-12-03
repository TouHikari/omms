# settings.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "your_password"
    MYSQL_SERVER: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "medical_system"

    DB_SSL: bool = False
    SSL_CA: str | None = None
    SSL_CERT: str | None = None
    SSL_KEY: str | None = None

    class Config:
        env_prefix = ""
        extra = "ignore"

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    def connect_args(self) -> dict:
        if self.DB_SSL:
            ssl = {}
            if self.SSL_CA: ssl["ca"] = self.SSL_CA
            if self.SSL_CERT: ssl["cert"] = self.SSL_CERT
            if self.SSL_KEY: ssl["key"] = self.SSL_KEY
            return {"ssl": ssl} if ssl else {"ssl": True}
        return {}

settings = Settings()