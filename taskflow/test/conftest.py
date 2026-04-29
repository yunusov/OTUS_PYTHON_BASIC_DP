# test/conftest.py

import sys
import os
import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

# Добавляем пути к проекту для импорта моделей
sys.path.insert(0, ".")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.database import BaseOrm
from src.core.dependencies import get_db_session
from src.core.config import settings
from src.models import UserOrm, ProjectOrm, TaskOrm  # явно импортируем все ORM
from main import app
from src.schemas.project import ProjectType

@pytest.fixture
def db_session():
    # Создаём in-memory SQLite, чтобы тесты не трогали прод БД
    engine = create_engine(
        url="sqlite:///:memory:",
        echo=True,  # включим logging, чтобы видеть SQL (для отладки)
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Сбрасываем старую схему (если была) и создаём с нуля
    BaseOrm.metadata.drop_all(bind=engine)  # 1. Убрать всё
    BaseOrm.metadata.create_all(bind=engine, checkfirst=True)  # 2. Создать таблицы tf_users, tf_projects, tf_tasks
    # 3. Очищать метаданные .clear() НЕ НАДО — это удаляет модели!

    # Конфигурируем ORM сессию
    sync_session = sessionmaker(bind=engine, expire_on_commit=False)
    with sync_session() as session:
        yield session  # возвращаем сессию как фикстуру

    # На всякий случай уничтожаем engine
    engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    # Мокаем FastAPI зависимость get_db_session на тестовую сессию
    app.dependency_overrides[get_db_session] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()  # Возвращаем всё как было после теста


@pytest.fixture
def server_url():
    return f"http://{settings.SERVER_IP}:{settings.SERVER_PORT}"


@pytest.fixture(scope="module")
def user_json():
    # Данные для теста регистрации пользователя
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
    # Данные для модификации
    return {
        "id": 1,
        "username": "USERNAME",
        "fullname": "FULLNAME",
        "email": "user123@example.com",
        "hashed_password": "string123",
        "is_active": False,
        "created_at": "2026-01-01T10:23:12.012Z",
    }




@pytest.fixture
def project_json():
    return {
        "name": "New project",
        "description": "Test description",
        "project_type": "software",
        "creator_id": 1,
        "created_at": "2026-01-01T10:23:12.012Z",
        "updated_at": "2026-01-01T10:23:12.012Z",
        "id":1
    }