import pytest
import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.services.file_service import FileService
from app.core.config import settings

client = TestClient(app)


def test_file_service_path_sanitization():
    project_id = uuid.uuid4()
    task_id = uuid.uuid4()

    # Valid file save
    rel_path, category, content_hash = FileService.save_file(
        project_id=project_id,
        task_id=task_id,
        category="backend",
        file_name="app/main.py",
        content="print('hello')"
    )
    assert category == "backend"
    assert rel_path.startswith(f"{project_id}/{task_id}/backend/")

    # Path traversal attack check - basename prevents escaping
    rel_path_2, category_2, hash_2 = FileService.save_file(
        project_id=project_id,
        task_id=task_id,
        category="frontend",
        file_name="../../../etc/passwd",
        content="malicious"
    )
    assert "passwd" in rel_path_2
    assert "../" not in rel_path_2


def test_artifact_apis_and_authorization():
    settings.LLM_MOCK_MODE = True

    # User 1 Setup
    u1_email = f"u1_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={"username": "user1", "email": u1_email, "password": "password123"})
    t1 = client.post("/api/auth/login", json={"email": u1_email, "password": "password123"}).json()["access_token"]
    h1 = {"Authorization": f"Bearer {t1}"}

    # User 2 Setup
    u2_email = f"u2_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={"username": "user2", "email": u2_email, "password": "password123"})
    t2 = client.post("/api/auth/login", json={"email": u2_email, "password": "password123"}).json()["access_token"]
    h2 = {"Authorization": f"Bearer {t2}"}

    # User 1 creates project & task
    p1 = client.post("/api/projects", json={"name": "P1 App", "description": "Desc"}, headers=h1).json()
    p1_id = p1["id"]

    start_res = client.post("/api/orchestrator/start", json={"project_id": p1_id, "user_prompt": "Build SaaS"}, headers=h1)
    task_id = start_res.json()["task_id"]

    # User 1 lists project artifacts
    art_res = client.get(f"/api/projects/{p1_id}/artifacts", headers=h1)
    assert art_res.status_code == 200
    artifacts = art_res.json()
    assert len(artifacts) > 0
    art_id = artifacts[0]["id"]

    # User 1 downloads artifact
    dl_res = client.get(f"/api/projects/{p1_id}/artifacts/{art_id}/download", headers=h1)
    assert dl_res.status_code == 200

    # User 2 tries to list User 1's project artifacts -> 404/unauthorized
    unauth_list = client.get(f"/api/projects/{p1_id}/artifacts", headers=h2)
    assert unauth_list.status_code == 404

    # User 2 tries to download User 1's artifact -> 404/unauthorized
    unauth_dl = client.get(f"/api/projects/{p1_id}/artifacts/{art_id}/download", headers=h2)
    assert unauth_dl.status_code == 404
