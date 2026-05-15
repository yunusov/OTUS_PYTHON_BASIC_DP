# test/conftest.py

import pytest

from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from main import main_app
from src.core import database
from src.core.async_session_wrapper import AsyncSessionWrapper
from src.models import BaseOrm, UserOrm  # noqa
from src.core.config import settings
from src.core import dependencies


@pytest.fixture(scope="session")
def db_session():
    # Создаём in-memory SQLite, чтобы тесты не трогали прод БД
    engine = create_engine(
        settings.TEST_DB_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    BaseOrm.metadata.create_all(bind=engine)
    sync_session = sessionmaker(
        engine,
        class_=Session,
        expire_on_commit=False,
        autoflush=True
    )
    with sync_session() as session:
        yield session  

    engine.dispose()


@pytest.fixture(scope="session")
def client(db_session):
        # Синхронный override
    def override_get_db_session():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    main_app.dependency_overrides.clear()
    main_app.dependency_overrides[dependencies.get_db_session] = override_get_db_session
    
    # Async override для fastapi_users
    async def override_get_async_session():
        yield AsyncSessionWrapper(db_session)
    
    main_app.dependency_overrides[database.get_db_helper().get_session] = override_get_async_session
    yield TestClient(main_app)

    main_app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def server_url():
    return f"http://{settings.run.SERVER_IP}:{settings.run.SERVER_PORT}/"

@pytest.fixture(scope="module")
def register_url(server_url):
    return "".join([f"{server_url}", settings.api.register_url])


@pytest.fixture(scope="session")
def user_json():
    # Данные для теста регистрации пользователя
    return {
        "email": "user@example.com",
        "password": "123",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "user",
        "fullname": "user",
    }

@pytest.fixture(scope="module")
def excluded_list() -> list:
    return [
        "created_at",
        "updated_at",
        "id",
        "password",
        "is_verified",
        "due_date",
    ]