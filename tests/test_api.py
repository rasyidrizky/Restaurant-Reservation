import uuid
import pytest
from src.core.security import get_current_user
from main import app

# --- Helper Data ---
def get_valid_payload():
    return {
        "customer_id": str(uuid.uuid4()),
        "contact_info": {
            "name": "Budi",
            "phone": "0812345",
            "email": "budi@test.com"
        },
        "start_time": "2025-12-31T19:00:00",
        "duration_minutes": 90
    }

# --- TEST AUTH ---
def test_login_success(client):
    response = client.post(
        "/api/token",
        data={"username": "admin", "password": "password123"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_fail(client):
    response = client.post(
        "/api/token",
        data={"username": "admin", "password": "wrongpassword"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401

# --- TEST CRUD (Tanpa Celery) ---

def test_create_reservation(client, auth_headers):
    payload = get_valid_payload()
    response = client.post("/api/reservations", json=payload, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "PENDING"
    assert "reservation_id" in data
    
    assert data["customer_details"]["name"] == "Budi"
    assert data["booking_info"]["duration_minutes"] == 90
    assert data["payment_info"]["status"] == "UNPAID"

def test_get_reservation_success(client, auth_headers):
    create_res = client.post("/api/reservations", json=get_valid_payload(), headers=auth_headers)
    res_id = create_res.json()["reservation_id"]
    
    response = client.get(f"/api/reservations/{res_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["reservation_id"] == res_id
    assert response.json()["customer_details"]["email"] == "budi@test.com"

def test_get_reservation_not_found(client, auth_headers):
    random_id = str(uuid.uuid4())
    response = client.get(f"/api/reservations/{random_id}", headers=auth_headers)
    assert response.status_code == 404

# --- TEST LIST & FILTER (Endpoint Baru) ---

def test_list_reservations(client, auth_headers):
    client.post("/api/reservations", json=get_valid_payload(), headers=auth_headers)
    client.post("/api/reservations", json=get_valid_payload(), headers=auth_headers)
    
    response = client.get("/api/reservations", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2
    
    response = client.get("/api/reservations?status=PENDING", headers=auth_headers)
    assert response.status_code == 200
    for res in response.json():
        assert res["status"] == "PENDING"

# --- TEST FULL BUSINESS FLOW (Confirm -> CheckIn -> Complete) ---

def test_full_business_flow(client, auth_headers):
    res = client.post("/api/reservations", json=get_valid_payload(), headers=auth_headers).json()
    res_id = res["reservation_id"]
    
    resp = client.post(f"/api/reservations/{res_id}/confirm", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "CONFIRMED"
    
    resp = client.post(f"/api/reservations/{res_id}/check-in", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "CHECKED_IN"
    
    resp = client.post(f"/api/reservations/{res_id}/complete", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETED"
    
    stats = client.get("/api/stats", headers=auth_headers).json()
    assert stats["completed_count"] >= 1

# --- TEST LOGIC ERRORS & EDGE CASES ---

def test_invalid_checkin_flow(client, auth_headers):
    res = client.post("/api/reservations", json=get_valid_payload(), headers=auth_headers).json()
    res_id = res["reservation_id"]
    
    resp = client.post(f"/api/reservations/{res_id}/check-in", headers=auth_headers)
    assert resp.status_code == 400
    assert "must be CONFIRMED" in resp.json()["detail"]

def test_assign_table_success(client, auth_headers):
    res = client.post("/api/reservations", json=get_valid_payload(), headers=auth_headers).json()
    res_id = res["reservation_id"]
    
    payload = {
        "table_id": str(uuid.uuid4()),
        "capacity": 4,
        "area": "Indoor"
    }
    response = client.post(f"/api/reservations/{res_id}/assign-table", json=payload, headers=auth_headers)
    assert response.status_code == 200
    
    get_res = client.get(f"/api/reservations/{res_id}", headers=auth_headers)
    assert get_res.json()["table_area"] == "Indoor"

def test_cancel_reservation_success(client, auth_headers):
    res = client.post("/api/reservations", json=get_valid_payload(), headers=auth_headers).json()
    res_id = res["reservation_id"]
    
    payload = {"reason_code": "REQ", "description": "Changed mind"}
    response = client.post(f"/api/reservations/{res_id}/cancel", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"

def test_unauthorized_access(client):
    app.dependency_overrides.pop(get_current_user, None)
    
    response = client.get(f"/api/reservations/{uuid.uuid4()}")
    assert response.status_code == 401