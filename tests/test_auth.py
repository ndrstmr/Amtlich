from datetime import datetime

from backend.models import UserRole


def test_auth_me_requires_authentication(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 403


def test_register_user_success(client, fake_db, mock_firebase, seed_user):
    payload = {
        "firebase_uid": "newuid",
        "email": "new@example.com",
        "name": "New User",
    }
    headers = {"Authorization": "Bearer faketoken"}
    response = client.post("/api/auth/register", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert payload["firebase_uid"] in fake_db.users.storage
    stored = fake_db.users.storage[payload["firebase_uid"]]
    assert stored["role"] == UserRole.VIEWER.value


def test_auth_me_with_mocked_firebase(client, mock_firebase, seed_user):
    headers = {"Authorization": "Bearer faketoken"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["firebase_uid"] == seed_user["firebase_uid"]


def test_register_user_requires_admin(client, fake_db, monkeypatch):
    from firebase_admin import auth as firebase_auth

    def fake_verify(token):
        return {"uid": "vieweruid"}

    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)

    viewer_doc = {
        "id": "viewer1",
        "firebase_uid": "vieweruid",
        "email": "viewer@example.com",
        "name": "Viewer",
        "role": UserRole.VIEWER.value,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True,
    }
    fake_db.users.storage[viewer_doc["firebase_uid"]] = viewer_doc

    payload = {
        "firebase_uid": "newviewer",
        "email": "newviewer@example.com",
        "name": "New Viewer",
    }

    headers = {"Authorization": "Bearer viewertoken"}
    response = client.post("/api/auth/register", json=payload, headers=headers)
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["message"] == "Insufficient permissions"
