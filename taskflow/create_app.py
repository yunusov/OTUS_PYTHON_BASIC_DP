from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqladmin import Admin
from src.core import get_db_helper, settings
from src.admin import register_admin_views
from src.admin.authentication import AdminAuth



@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await get_db_helper().dispose()


def create() -> FastAPI:
    app = FastAPI(lifespan=lifespan)




    admin = Admin(
        app=app,
        authentication_backend=AdminAuth(secret_key=settings.run.SECRET_KEY),
        session_maker=get_db_helper().session_factory,
        templates_dir="src/templates/admin",
    )
    register_admin_views(admin)

    return app
