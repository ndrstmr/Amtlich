import os
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

# Ensure environment variables so server initializes
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "testdb")
os.environ.setdefault("FIREBASE_SERVICE_ACCOUNT", "{}")
os.environ.setdefault("ALLOWED_ORIGINS", "http://testserver")

from backend.models import UserRole  # noqa: E402
from backend.server import app  # noqa: E402
from backend.services import db as db_module  # noqa: E402


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

    async def count_documents(self, query):
        return len(self.storage)

    async def update_one(self, query, update):
        key = query.get("id") or query.get("firebase_uid")
        doc = self.storage.get(key)
        if doc:
            doc.update(update.get("$set", {}))
            return AsyncMock(modified_count=1)
        return AsyncMock(modified_count=0)

    async def delete_one(self, query):
        key = query.get("id") or query.get("firebase_uid")
        if key in self.storage:
            del self.storage[key]
            return AsyncMock(deleted_count=1)
        return AsyncMock(deleted_count=0)

    def find(self):
        class Cursor:
            def __init__(self, docs):
                self.docs = list(docs.values())

            async def to_list(self, limit):
                return self.docs[:limit]

        return Cursor(self.storage)


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
    from backend import auth
    from backend.routes import api as api_routes

    monkeypatch.setattr(auth, "db", db)
    monkeypatch.setattr(api_routes, "db", db)
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
