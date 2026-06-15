from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqladmin import Admin
from src.core import get_db_helper, settings
from src.admin import register_admin_views
from src.admin.authentication import AdminAuth
from src.email_parser.scheduler import EmailScheduler



@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await get_db_helper().dispose()

def start_email_scheduler():
    if settings.run.EMAIL_SCHEDULER:
        EmailScheduler().start()


def create() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    admin = Admin(
        app=app,
        authentication_backend=AdminAuth(secret_key=settings.run.SECRET_KEY),
        session_maker=get_db_helper().session_factory,
        templates_dir="src/templates/admin",
    )
    register_admin_views(admin)
    start_email_scheduler()

    return app
