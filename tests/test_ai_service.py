from datetime import datetime

import httpx
import pytest
from fastapi import HTTPException

from backend.models import User, UserRole
from backend.services.ai import AIService, AIServiceError
from backend.services.tools import GenerateTextTool


class DummyClient:
    def __init__(self, side_effects):
        self.side_effects = side_effects
        self.attempts = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def post(self, url, json=None, headers=None):
        self.attempts += 1
        effect = self.side_effects.pop(0)
        if isinstance(effect, Exception):
            raise effect
        return effect


class DummyResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=None)

    def json(self):
        return self._data


@pytest.mark.asyncio
async def test_ai_service_retries_and_fails(monkeypatch):
    client = DummyClient(
        [httpx.TimeoutException("timeout"), httpx.TimeoutException("timeout")]
    )
    monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: client)
    service = AIService(
        base_url="http://example.com", api_key="key", retries=2, timeout=1
    )
    with pytest.raises(AIServiceError):
        await service.post("/endpoint", {"prompt": "hi"})
    assert client.attempts == 2


@pytest.mark.asyncio
async def test_generate_text_tool_error(monkeypatch):
    async def fail_post(*args, **kwargs):
        raise AIServiceError("boom")

    service = AIService()
    monkeypatch.setattr(service, "post", fail_post)
    tool = GenerateTextTool(service)
    user = User(
        id="u1",
        firebase_uid="f1",
        email="a@example.com",
        name="User",
        role=UserRole.ADMIN,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    with pytest.raises(HTTPException) as exc:
        await tool.execute({"prompt": "hi"}, user)
    assert exc.value.status_code == 502
    assert exc.value.detail["code"] == "ai_service_error"
