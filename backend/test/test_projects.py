import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_projects_crud_flow():
    unique_email = f"proj_user_{uuid.uuid4().hex[:8]}@example.com"
    password = "securepassword123"

    # Register & Login
    client.post("/api/auth/register", json={"username": "projuser", "email": unique_email, "password": password})
    login_res = client.post("/api/auth/login", json={"email": unique_email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Project
    create_res = client.post(
        "/api/projects",
        json={"name": "E-Commerce AI Platform", "description": "AI-powered web shop"},
        headers=headers
    )
    assert create_res.status_code == 201
    project_data = create_res.json()
    project_id = project_data["id"]
    assert project_data["name"] == "E-Commerce AI Platform"

    # 2. List User Projects
    list_res = client.get("/api/projects", headers=headers)
    assert list_res.status_code == 200
    projects_list = list_res.json()
    assert len(projects_list) >= 1

    # 3. Get Single Project
    get_res = client.get(f"/api/projects/{project_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == project_id

    # 4. Delete Project
    del_res = client.delete(f"/api/projects/{project_id}", headers=headers)
    assert del_res.status_code == 204
