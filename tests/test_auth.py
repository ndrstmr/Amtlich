import os
from fastapi.testclient import TestClient

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "testdb")
os.environ.setdefault("FIREBASE_SERVICE_ACCOUNT", "{}")

from backend.server import app

client = TestClient(app)

def test_auth_me_requires_authentication():
    response = client.get("/api/auth/me")
    assert response.status_code == 401
