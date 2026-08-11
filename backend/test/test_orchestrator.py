import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.database.database import SessionLocal
from app.database.models import TaskExecution

client = TestClient(app)


def test_orchestrator_full_workflow_mock():
    # Enable mock mode for test execution
    settings.LLM_MOCK_MODE = True

    # Setup test user and project
    unique_email = f"orch_user_{uuid.uuid4().hex[:8]}@example.com"
    password = "securepassword123"

    client.post("/api/auth/register", json={"username": "orchuser", "email": unique_email, "password": password})
    login_res = client.post("/api/auth/login", json={"email": unique_email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_proj_res = client.post("/api/projects", json={"name": "Task System", "description": "Test Project"}, headers=headers)
    project_id = create_proj_res.json()["id"]

    # 1. Start Task API (Background task runs automatically in TestClient)
    start_res = client.post(
        "/api/orchestrator/start",
        json={"project_id": project_id, "user_prompt": "Build a task tracker app"},
        headers=headers
    )
    assert start_res.status_code == 202
    task_id = start_res.json()["task_id"]

    # 2. Check Status API
    status_res = client.get(f"/api/orchestrator/status/{task_id}", headers=headers)
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["status"] == "completed"
    assert len(status_data["logs"]) == 12

    # 3. Check Results API
    results_res = client.get(f"/api/orchestrator/results/{task_id}", headers=headers)
    assert results_res.status_code == 200
    results_data = results_res.json()
    assert results_data["status"] == "completed"
    assert results_data["total_artifacts"] > 0


def test_task_cancellation_flow():
    settings.LLM_MOCK_MODE = True

    unique_email = f"cancel_user_{uuid.uuid4().hex[:8]}@example.com"
    password = "securepassword123"

    client.post("/api/auth/register", json={"username": "canceluser", "email": unique_email, "password": password})
    login_res = client.post("/api/auth/login", json={"email": unique_email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_proj_res = client.post("/api/projects", json={"name": "Cancel System", "description": "Cancel Test Project"}, headers=headers)
    project_id = create_proj_res.json()["id"]

    # 1. Create a running task execution directly in DB
    db = SessionLocal()
    try:
        user_res = client.get("/api/auth/profile", headers=headers)
        user_id = user_res.json()["id"]

        task = TaskExecution(
            project_id=uuid.UUID(project_id),
            user_id=uuid.UUID(user_id),
            user_prompt="Long running task to cancel",
            status="running"
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = str(task.id)
    finally:
        db.close()

    # 2. Call Cancel API
    cancel_res = client.post(f"/api/orchestrator/cancel/{task_id}", headers=headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"


