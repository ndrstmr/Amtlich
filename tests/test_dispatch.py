from fastapi.testclient import TestClient
from backend.server import app
from backend.services.tools import tool_registry, Tool

client = TestClient(app)


class DummyTool(Tool):
    def get_name(self) -> str:
        return "dummyTool"

    async def execute(self, args, user):
        return {"echo": args, "user": user.id}


def test_tool_dispatch(client, mock_firebase, seed_user):
    tool = DummyTool()
    tool_registry.register(tool)
    try:
        headers = {"Authorization": "Bearer faketoken"}
        payload = {"tool": tool.get_name(), "args": {"a": 1}}
        response = client.post("/api/mcp/dispatch", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["echo"] == payload["args"]
        assert data["data"]["user"] == seed_user["id"]
    finally:
        tool_registry.tools.pop(tool.get_name(), None)


