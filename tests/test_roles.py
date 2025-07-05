from datetime import datetime

from backend.models import UserRole


def test_dashboard_stats_allows_admin(client, mock_firebase, seed_user):
    headers = {"Authorization": "Bearer faketoken"}
    response = client.get("/api/dashboard/stats", headers=headers)
    assert response.status_code == 200


def test_dashboard_stats_rejects_viewer(client, fake_db, monkeypatch):
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

    headers = {"Authorization": "Bearer viewertoken"}
    response = client.get("/api/dashboard/stats", headers=headers)
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["message"] == "Insufficient permissions"
