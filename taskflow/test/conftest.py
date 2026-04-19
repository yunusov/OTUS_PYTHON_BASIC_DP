import sys
import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

sys.path.insert(0, ".")

from src.core.database import BaseOrm, get_db_session
from src.core.config import settings
from src.models import UserOrm  # noqa
from main import app


@pytest.fixture
def db_session():
    engine = create_engine(
        url="sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    BaseOrm.metadata.create_all(bind=engine)
    sync_session = sessionmaker(
        engine,
        class_=Session,
        expire_on_commit=False,
    )
    with sync_session() as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides.clear()
    app.dependency_overrides[get_db_session] = override_get_db
    yield TestClient(app)

    app.dependency_overrides.clear()

@pytest.fixture
def server_url():
    return f"http://{settings.SERVER_IP}:{settings.SERVER_PORT}"

@pytest.fixture(scope="module")
def user_json():
    return {
        "id": 1,
        "username": "VVVV",
        "fullname": "VVVVVV",
        "email": "user@example.com",
        "hashed_password": "string",
        "is_active": True,
        "created_at": "2026-04-18T10:23:12.012Z",
    }

@pytest.fixture
def modify_json():
    return {
        "id": 1,
        "username": "USERNAME",
        "fullname": "FULLNAME",
        "email": "user123@example.com",
        "hashed_password": "string123",
        "is_active": False,
        "created_at": "2026-01-01T10:23:12.012Z",
    }
