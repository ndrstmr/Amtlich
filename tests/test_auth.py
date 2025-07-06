from backend.models import UserRole


def test_auth_me_requires_authentication(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 403


def test_register_user_success(client, fake_db):
    payload = {
        "firebase_uid": "newuid",
        "email": "new@example.com",
        "name": "New User",
    }
    response = client.post("/api/auth/register", json=payload)
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
