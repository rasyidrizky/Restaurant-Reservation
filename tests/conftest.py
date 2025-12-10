import pytest
from fastapi.testclient import TestClient
from main import app
from src.api.routes import reservation_db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    """Membersihkan database in-memory sebelum setiap test berjalan"""
    reservation_db.clear()
    yield

@pytest.fixture
def auth_headers(client):
    """Mendapatkan token admin untuk testing endpoint protected"""
    # Pastikan data user dummy sesuai dengan src/api/auth.py
    response = client.post(
        "/api/token",
        data={"username": "admin", "password": "password123"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}