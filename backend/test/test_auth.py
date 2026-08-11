import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_flow():
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    username = "testuser"
    password = "securepassword123"

    # 1. Register User
    reg_response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": unique_email,
            "password": password
        }
    )
    assert reg_response.status_code == 201
    data = reg_response.json()
    assert data["email"] == unique_email
    assert "id" in data

    # 2. Login User
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": unique_email,
            "password": password
        }
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]

    # 3. Get User Profile
    profile_response = client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["email"] == unique_email
