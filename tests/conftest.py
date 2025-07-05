import os
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

# Ensure environment variables so server initializes
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "testdb")
os.environ.setdefault("FIREBASE_SERVICE_ACCOUNT", "{}")

from backend.server import app
from backend.models import UserRole
from backend.services import db as db_module


class FakeCollection:
    def __init__(self):
        self.storage = {}

    async def find_one(self, query):
        if "firebase_uid" in query:
            return self.storage.get(query["firebase_uid"])
        if "id" in query:
            return self.storage.get(query["id"])
        return None

    async def insert_one(self, doc):
        key = doc.get("firebase_uid") or doc.get("id")
        self.storage[key] = doc
        return AsyncMock(inserted_id=key)


class FakeDB:
    def __init__(self):
        self.users = FakeCollection()
        self.pages = FakeCollection()
        self.articles = FakeCollection()
        self.categories = FakeCollection()


@pytest.fixture(autouse=True)
def fake_db(monkeypatch):
    db = FakeDB()
    monkeypatch.setattr(db_module, "db", db)
    yield db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_firebase(monkeypatch):
    from firebase_admin import auth as firebase_auth

    def fake_verify(token):
        return {"uid": "testuid"}

    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)


@pytest.fixture
def seed_user(fake_db):
    user_doc = {
        "id": "user1",
        "firebase_uid": "testuid",
        "email": "test@example.com",
        "name": "Test User",
        "role": UserRole.ADMIN.value,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
    }
    fake_db.users.storage[user_doc["firebase_uid"]] = user_doc
    return user_doc

