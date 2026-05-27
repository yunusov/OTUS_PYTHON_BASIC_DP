from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqladmin import Admin
from fastapi.responses import FileResponse
from src.core import get_db_helper, settings
from src.admin import register_admin_views
from src.admin.authentication import AdminAuth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await get_db_helper().dispose()


def register_favicon(app: FastAPI):
    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return FileResponse("src/images/info.png", media_type="image/png")


def create() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    register_favicon(app)

    admin = Admin(
        app=app,
        authentication_backend=AdminAuth(secret_key=settings.run.SECRET_KEY),
        session_maker=get_db_helper().session_factory,
        templates_dir="src/templates/admin",
    )
    register_admin_views(admin)
    return app
