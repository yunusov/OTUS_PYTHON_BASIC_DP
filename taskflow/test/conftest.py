# test/conftest.py

import pytest
import random

import requests
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from main import main_app
from src.core import database
from src.core.async_session_wrapper import AsyncSessionWrapper
from src.core.auth.user_manager import UserManager
from src.models import BaseOrm, UserOrm  # noqa
from src.core.config import settings
from src.core import dependencies
from src.utils.loguru_config import AppLogger

logger = AppLogger().get_logger()


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
        autoflush=True,
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

    main_app.dependency_overrides[database.get_db_helper().get_session] = (
        override_get_async_session
    )

    yield TestClient(main_app)

    main_app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def token(client, login_url, user_json, project_user, verify_url, verify_token):
    # login user
    resp: requests.Response = client.post(
        verify_url,
        json={"token": verify_token},
    )

    resp: requests.Response = client.post(
        login_url,
        data={
            "username": project_user["email"],  # username = email
            "password": user_json["password"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    logger.debug(f"Token: {resp.json()}")
    return resp.json()["access_token"]


@pytest.fixture(scope="module")
def verify_token(client, request_verify_token_url, project_user):
    original = UserManager.on_after_request_verify
    captured = {}

    # monkeypath on_after_request_verify
    async def capture_token(self, user, token, request=None):
        captured["token"] = token
        return await original(self, user, token, request)

    UserManager.on_after_request_verify = capture_token

    # request verify token
    logger.info(f"request_verify_token_url: {request_verify_token_url}")
    requests.Response = client.post(
        request_verify_token_url,
        json={
            "email": project_user["email"],
        },
    )
    logger.debug(f"Token: {captured}")
    yield captured["token"]

    UserManager.on_after_request_verify = original


@pytest.fixture(scope="module")
def project_user(client, register_url, user_json):
    """Создаёт пользователя и возвращает его ID"""
    json = user_json.copy()
    json["username"] = "".join([json["username"], str(random.randint(1, 1000))])
    json["fullname"] = json["username"]
    json["email"] = json["email"].replace("user", "u" + str(random.randint(1, 1000)))
    logger.info(json)
    resp: requests.Response = client.post(register_url, json=json)
    return resp.json()


@pytest.fixture(scope="module")
def request_verify_token_url(server_url):
    return "".join([f"{server_url}", settings.api.auth_url, "/request-verify-token"])


@pytest.fixture(scope="module")
def verify_url(server_url):
    return "".join([f"{server_url}", settings.api.auth_url, "/verify"])


@pytest.fixture(scope="module")
def server_url():
    return f"http://{settings.run.SERVER_IP}:{settings.run.SERVER_PORT}/"


@pytest.fixture(scope="module")
def register_url(server_url):
    return "".join([f"{server_url}", settings.api.register_url])


@pytest.fixture(scope="module")
def login_url(server_url):
    return "".join([f"{server_url}", settings.api.auth_url, "/login"])


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
        "owner",
        "assignee",
        "creator",
    ]
