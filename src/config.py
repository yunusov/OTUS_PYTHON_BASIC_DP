from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    MIDDLEWARE_SECRET_KEY: str
    SERVER_IP: str
    SERVER_PORT: str


    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def DATABASE_URL_ASYNC(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def SERVER_URL(self):
        return "http://" + self.SERVER_IP + ":" + self.SERVER_PORT


    model_config = SettingsConfigDict(env_file="src/.env")

settings = Settings()
