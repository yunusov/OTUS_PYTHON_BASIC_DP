from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = Path(__file__).parent / ".env"


class BaseConfig(BaseSettings):
    """Базовый класс для всех настроек, читающих из .env"""
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=ENV_FILE,
        extra="ignore",
    )


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    messages: str = "/messages"
    projects: str = "/projects"
    register_ep: str = "/register"
    service: str = "/service"
    tasks: str = "/tasks"
    users: str = "/users"
    logout: str = "/logout"
    login: str = "/login"


class ApiPrefix(BaseModel):
    PREFIX: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @property
    def bearer_token_url(self) -> str:
        # api/v1/auth/login
        parts = (self.PREFIX, self.v1.prefix, self.v1.auth, "/login")
        path = "".join(parts)
        return path.removeprefix("/")

    @property
    def register_url(self) -> str:
        # api/v1/auth/register
        parts = (self.PREFIX, self.v1.prefix, self.v1.auth, "/register")
        path = "".join(parts)
        return path.removeprefix("/")

    @property
    def auth_url(self) -> str:
        # api/v1/auth
        parts = (self.PREFIX, self.v1.prefix, self.v1.auth)
        path = "".join(parts)
        return path.removeprefix("/")
    
    @property
    def users_url(self) -> str:
        # api/v1/users
        parts = (self.PREFIX, self.v1.prefix, "/users")
        path = "".join(parts)
        return path.removeprefix("/")
    
    @property
    def projects_url(self) -> str:
        # api/v1/projects
        parts = (self.PREFIX, self.v1.prefix, "/projects")
        path = "".join(parts)
        return path.removeprefix("/")
    
    @property
    def tasks_url(self) -> str:
        # api/v1/tasks
        parts = (self.PREFIX, self.v1.prefix, "/tasks")
        path = "".join(parts)
        return path.removeprefix("/")


class RunConfig(BaseConfig):
    SECRET_KEY: str
    SERVER_IP: str = "0.0.0.0"
    SERVER_PORT: str = "8000"


class DBConfig(BaseConfig):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10

class EmailConfig(BaseConfig):
    email_host: str = "127.0.0.1"
    email_port: str = "1025"
    email_login: str = "admin@taskflow.com" 
    email_token: str = ""
    smtp_auth: bool = False


class AccessToken(BaseConfig):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class Settings(BaseConfig):       
    api: ApiPrefix = ApiPrefix()
    db: DBConfig = DBConfig()
    email: EmailConfig = EmailConfig()
    run: RunConfig = RunConfig()
    access_token: AccessToken = AccessToken()

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.db.DB_USER}:{self.db.DB_PASS}@{self.db.DB_HOST}:{self.db.DB_PORT}/{self.db.DB_NAME}"

    @property
    def DATABASE_URL_ASYNC(self):
        return f"postgresql+asyncpg://{self.db.DB_USER}:{self.db.DB_PASS}@{self.db.DB_HOST}:{self.db.DB_PORT}/{self.db.DB_NAME}"

    @property
    def SERVER_URL(self):
        return "http://" + self.run.SERVER_IP + ":" + self.run.SERVER_PORT

    @property
    def TEST_DB_URL(self):
        return "sqlite:///:memory:"


settings = Settings()
