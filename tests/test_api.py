import uuid
import pytest

def create_dummy_reservation(client, auth_headers):
    payload = {
        "customer_id": str(uuid.uuid4()),
        "contact_info": {
            "name": "Budi",
            "phone": "0812345",
            "email": "budi@test.com"
        },
        "start_time": "2025-12-31T19:00:00",
        "duration_minutes": 90
    }
    response = client.post("/api/reservations", json=payload, headers=auth_headers)
    return response.json()

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

def test_create_reservation(client, auth_headers):
    res = create_dummy_reservation(client, auth_headers)
    assert res["status"] == "PENDING"
    assert "reservation_id" in res

def test_get_reservation_success(client, auth_headers):
    res_data = create_dummy_reservation(client, auth_headers)
    res_id = res_data["reservation_id"]
    
    response = client.get(f"/api/reservations/{res_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["reservation_id"] == res_id

def test_get_reservation_not_found(client, auth_headers):
    random_id = str(uuid.uuid4())
    response = client.get(f"/api/reservations/{random_id}", headers=auth_headers)
    assert response.status_code == 404

def test_confirm_reservation_success(client, auth_headers):
    res_data = create_dummy_reservation(client, auth_headers)
    res_id = res_data["reservation_id"]
    
    response = client.post(f"/api/reservations/{res_id}/confirm", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"

def test_confirm_reservation_not_found(client, auth_headers):
    random_id = str(uuid.uuid4())
    response = client.post(f"/api/reservations/{random_id}/confirm", headers=auth_headers)
    assert response.status_code == 404

def test_assign_table_success(client, auth_headers):
    res_data = create_dummy_reservation(client, auth_headers)
    res_id = res_data["reservation_id"]
    
    payload = {
        "table_id": str(uuid.uuid4()),
        "capacity": 4,
        "area": "Indoor"
    }
    response = client.post(f"/api/reservations/{res_id}/assign-table", json=payload, headers=auth_headers)
    assert response.status_code == 200
    
    get_res = client.get(f"/api/reservations/{res_id}", headers=auth_headers)
    assert get_res.json()["table_area"] == "Indoor"

def test_assign_table_not_found(client, auth_headers):
    random_id = str(uuid.uuid4())
    payload = {"table_id": str(uuid.uuid4()), "capacity": 4, "area": "Indoor"}
    response = client.post(f"/api/reservations/{random_id}/assign-table", json=payload, headers=auth_headers)
    assert response.status_code == 404

def test_cancel_reservation_success(client, auth_headers):
    res_data = create_dummy_reservation(client, auth_headers)
    res_id = res_data["reservation_id"]
    
    payload = {"reason_code": "REQ", "description": "Changed mind"}
    response = client.post(f"/api/reservations/{res_id}/cancel", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"

def test_cancel_reservation_not_found(client, auth_headers):
    random_id = str(uuid.uuid4())
    payload = {"reason_code": "REQ", "description": "Changed mind"}
    response = client.post(f"/api/reservations/{random_id}/cancel", json=payload, headers=auth_headers)
    assert response.status_code == 404

def test_domain_error_propagation(client, auth_headers):
    res_data = create_dummy_reservation(client, auth_headers)
    res_id = res_data["reservation_id"]
    
    payload = {"reason_code": "REQ", "description": "Changed mind"}
    client.post(f"/api/reservations/{res_id}/cancel", json=payload, headers=auth_headers)
    
    response = client.post(f"/api/reservations/{res_id}/confirm", headers=auth_headers)
    assert response.status_code == 400

def test_unauthorized_access(client):
    response = client.get(f"/api/reservations/{uuid.uuid4()}")
    assert response.status_code == 401