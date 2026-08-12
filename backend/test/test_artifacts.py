import pytest
import uuid
import zipfile
import io
from fastapi.testclient import TestClient

from app.main import app
from app.services.file_service import FileService
from app.services.validation_service import ValidationService
from app.core.config import settings

client = TestClient(app)


def test_file_service_nested_paths_and_sanitization():
    project_id = uuid.uuid4()
    task_id = uuid.uuid4()

    # Valid nested path file save
    rel_path, clean_fname, category, content_hash = FileService.save_file(
        project_id=project_id,
        task_id=task_id,
        category="frontend",
        file_path="frontend/src/App.tsx",
        content="export default function App() { return <div>App</div>; }"
    )
    assert category == "frontend"
    assert rel_path == "frontend/src/App.tsx"
    assert clean_fname == "App.tsx"

    # Path traversal attack check - escaping prefix stripped safely
    rel_path_2, clean_fname_2, category_2, hash_2 = FileService.save_file(
        project_id=project_id,
        task_id=task_id,
        category="backend",
        file_path="../../../etc/passwd",
        content="malicious"
    )
    assert clean_fname_2 == "passwd"
    assert not rel_path_2.startswith("../")


def test_validation_service_ast_and_security():
    # Valid Python code
    valid_res = ValidationService.validate_code("main.py", "def foo():\n    return 42\n")
    assert valid_res["valid"] is True
    assert len(valid_res["errors"]) == 0

    # Invalid Python syntax
    invalid_res = ValidationService.validate_code("broken.py", "def foo(\n")
    assert invalid_res["valid"] is False
    assert len(invalid_res["errors"]) > 0

    # Security risk scan
    risks = ValidationService.scan_security_risks("unsafe.py", 'os.system(user_input)\nsecret_key = "mysecretkey123"')
    assert len(risks) >= 2


def test_artifact_apis_zip_download_and_authorization():
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

    # User 1 downloads single artifact
    dl_res = client.get(f"/api/projects/{p1_id}/artifacts/{art_id}/download", headers=h1)
    assert dl_res.status_code == 200

    # User 1 downloads Project ZIP archive
    zip_res = client.get(f"/api/projects/{p1_id}/download-zip", headers=h1)
    assert zip_res.status_code == 200
    assert zip_res.headers["content-type"] == "application/zip"

    # Verify ZIP buffer contains valid files
    zip_file = zipfile.ZipFile(io.BytesIO(zip_res.content))
    assert len(zip_file.namelist()) > 0

    # User 1 downloads Task ZIP archive
    task_zip_res = client.get(f"/api/orchestrator/results/{task_id}/download-zip", headers=h1)
    assert task_zip_res.status_code == 200

    # User 2 tries to list User 1's project artifacts -> 404/unauthorized
    unauth_list = client.get(f"/api/projects/{p1_id}/artifacts", headers=h2)
    assert unauth_list.status_code == 404

    # User 2 tries to download User 1's ZIP -> 404/unauthorized
    unauth_zip = client.get(f"/api/projects/{p1_id}/download-zip", headers=h2)
    assert unauth_zip.status_code == 404
