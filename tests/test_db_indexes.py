import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.services import db as db_module

@pytest.mark.asyncio
async def test_ensure_indexes(monkeypatch):
    users = MagicMock()
    users.create_index = AsyncMock()
    pages = MagicMock()
    pages.create_index = AsyncMock()
    articles = MagicMock()
    articles.create_index = AsyncMock()

    fake_db = MagicMock(users=users, pages=pages, articles=articles)
    monkeypatch.setattr(db_module, "db", fake_db)

    await db_module.ensure_indexes()

    users.create_index.assert_any_call("firebase_uid", unique=True)
    users.create_index.assert_any_call("id", unique=True)
    users.create_index.assert_any_call("email")

    pages.create_index.assert_any_call("id", unique=True)
    pages.create_index.assert_any_call("slug")

    articles.create_index.assert_any_call("id", unique=True)
    articles.create_index.assert_any_call("slug")
