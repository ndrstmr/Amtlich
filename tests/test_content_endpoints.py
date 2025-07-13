import datetime
from backend.models import UserRole


def test_create_page(client, mock_firebase, seed_user):
    payload = {"title": "Test Page", "slug": "test-page", "content": "Body"}
    headers = {"Authorization": "Bearer faketoken"}
    response = client.post("/api/pages", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]


def test_update_page_by_author(client, fake_db, monkeypatch):
    from firebase_admin import auth as firebase_auth

    def fake_verify(token):
        return {"uid": "authoruid"}

    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)

    author_doc = {
        "id": "author1",
        "firebase_uid": "authoruid",
        "email": "a@example.com",
        "name": "Author",
        "role": UserRole.AUTHOR.value,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
        "is_active": True,
    }
    fake_db.users.storage[author_doc["firebase_uid"]] = author_doc

    page_doc = {
        "id": "page1",
        "title": "Old",
        "slug": "old",
        "content": "c",
        "author_id": author_doc["id"],
        "status": "draft",
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }
    fake_db.pages.storage[page_doc["id"]] = page_doc

    headers = {"Authorization": "Bearer token"}
    response = client.put(
        f"/api/pages/{page_doc['id']}",
        json={"title": "New"},
        headers=headers,
    )
    assert response.status_code == 200
    assert fake_db.pages.storage[page_doc["id"]]["title"] == "New"


def test_delete_article_as_editor(client, fake_db, monkeypatch):
    from firebase_admin import auth as firebase_auth

    def fake_verify(token):
        return {"uid": "editoruid"}

    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)

    editor_doc = {
        "id": "editor1",
        "firebase_uid": "editoruid",
        "email": "e@example.com",
        "name": "Editor",
        "role": UserRole.EDITOR.value,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
        "is_active": True,
    }
    fake_db.users.storage[editor_doc["firebase_uid"]] = editor_doc

    article_doc = {
        "id": "art1",
        "title": "T",
        "slug": "t",
        "content": "c",
        "author_id": editor_doc["id"],
        "status": "draft",
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }
    fake_db.articles.storage[article_doc["id"]] = article_doc

    headers = {"Authorization": "Bearer token"}
    response = client.delete(f"/api/articles/{article_doc['id']}", headers=headers)
    assert response.status_code == 200
    assert article_doc["id"] not in fake_db.articles.storage


def test_create_article(client, mock_firebase, seed_user):
    payload = {"title": "Test Article", "slug": "test-article", "content": "Body"}
    headers = {"Authorization": "Bearer faketoken"}
    response = client.post("/api/articles", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]


def test_update_article_by_author(client, fake_db, monkeypatch):
    from firebase_admin import auth as firebase_auth

    def fake_verify(token):
        return {"uid": "authoruid"}

    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)

    author_doc = {
        "id": "author2",
        "firebase_uid": "authoruid",
        "email": "author2@example.com",
        "name": "Author2",
        "role": UserRole.AUTHOR.value,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
        "is_active": True,
    }
    fake_db.users.storage[author_doc["firebase_uid"]] = author_doc

    article_doc = {
        "id": "art2",
        "title": "Old",
        "slug": "old",
        "content": "c",
        "author_id": author_doc["id"],
        "status": "draft",
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }
    fake_db.articles.storage[article_doc["id"]] = article_doc

    headers = {"Authorization": "Bearer token"}
    response = client.put(
        f"/api/articles/{article_doc['id']}",
        json={"title": "New"},
        headers=headers,
    )
    assert response.status_code == 200
    assert fake_db.articles.storage[article_doc["id"]]["title"] == "New"


def test_delete_page_as_editor(client, fake_db, monkeypatch):
    from firebase_admin import auth as firebase_auth

    def fake_verify(token):
        return {"uid": "editoruid"}

    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)

    editor_doc = {
        "id": "editor2",
        "firebase_uid": "editoruid",
        "email": "editor2@example.com",
        "name": "Editor2",
        "role": UserRole.EDITOR.value,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
        "is_active": True,
    }
    fake_db.users.storage[editor_doc["firebase_uid"]] = editor_doc

    page_doc = {
        "id": "page2",
        "title": "Old",
        "slug": "old",
        "content": "c",
        "author_id": editor_doc["id"],
        "status": "draft",
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    }
    fake_db.pages.storage[page_doc["id"]] = page_doc

    headers = {"Authorization": "Bearer token"}
    response = client.delete(f"/api/pages/{page_doc['id']}", headers=headers)
    assert response.status_code == 200
    assert page_doc["id"] not in fake_db.pages.storage


def test_create_page_denied_for_viewer(client, fake_db, monkeypatch):
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
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
        "is_active": True,
    }
    fake_db.users.storage[viewer_doc["firebase_uid"]] = viewer_doc

    payload = {"title": "Denied", "slug": "denied", "content": "c"}
    headers = {"Authorization": "Bearer viewertoken"}
    response = client.post("/api/pages", json=payload, headers=headers)
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["message"] == "Insufficient permissions"


def test_create_article_denied_for_viewer(client, fake_db, monkeypatch):
    from firebase_admin import auth as firebase_auth

    def fake_verify(token):
        return {"uid": "vieweruid"}

    monkeypatch.setattr(firebase_auth, "verify_id_token", fake_verify)

    viewer_doc = {
        "id": "viewer2",
        "firebase_uid": "vieweruid",
        "email": "viewer2@example.com",
        "name": "Viewer2",
        "role": UserRole.VIEWER.value,
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
        "is_active": True,
    }
    fake_db.users.storage[viewer_doc["firebase_uid"]] = viewer_doc

    payload = {"title": "Denied", "slug": "denied", "content": "c"}
    headers = {"Authorization": "Bearer viewertoken"}
    response = client.post("/api/articles", json=payload, headers=headers)
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["message"] == "Insufficient permissions"
