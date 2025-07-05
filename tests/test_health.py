import os
from fastapi.testclient import TestClient

# Ensure required environment variables for db init
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "testdb")
os.environ.setdefault("FIREBASE_SERVICE_ACCOUNT", "{}")

from backend.server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
