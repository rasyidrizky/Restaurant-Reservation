import uuid
import pytest
from datetime import datetime
from src.domain.models import Reservation
from src.domain.value_objects import ContactInfo, ReservationTime, ReservationPolicy, CancellationReason, ReservationStatus

# Helper Setup
@pytest.fixture
def sample_reservation():
    contact = ContactInfo(name="Test", phone="123", email="test@example.com")
    time_vo = ReservationTime(start_time=datetime.now(), duration_minutes=90)
    return Reservation(
        customer_id=uuid.uuid4(),
        contact_info=contact,
        reservation_time=time_vo,
        policy=ReservationPolicy()
    )

def test_reservation_creation(sample_reservation):
    assert sample_reservation.status == "PENDING"
    assert len(sample_reservation.domain_events) == 1 

def test_confirm_reservation_logic(sample_reservation):
    sample_reservation.confirm_reservation()
    assert sample_reservation.status == "CONFIRMED"
    assert len(sample_reservation.domain_events) == 2

def test_assign_table_logic(sample_reservation):
    sample_reservation.assign_table(uuid.uuid4(), 4, "Outdoor")
    assert sample_reservation.table_assignment is not None
    assert sample_reservation.table_assignment.area == "Outdoor"

def test_cancel_reservation_logic(sample_reservation):
    reason = CancellationReason(reason_code="TEST", description="Testing")
    sample_reservation.cancel_reservation(reason)
    assert sample_reservation.status == "CANCELLED"

def test_cannot_confirm_cancelled_reservation(sample_reservation):
    reason = CancellationReason(reason_code="TEST", description="Testing")
    sample_reservation.cancel_reservation(reason)
    
    with pytest.raises(ValueError):
        sample_reservation.confirm_reservation()

def test_cannot_assign_table_to_cancelled_reservation(sample_reservation):
    reason = CancellationReason(reason_code="TEST", description="Testing")
    sample_reservation.cancel_reservation(reason)
    
    with pytest.raises(ValueError):
        sample_reservation.assign_table(uuid.uuid4(), 4, "Indoor")

def test_cannot_cancel_completed_reservation(sample_reservation):
    sample_reservation.status = ReservationStatus.COMPLETED
    
    reason = CancellationReason(reason_code="TEST", description="Testing")
    with pytest.raises(ValueError):
        sample_reservation.cancel_reservation(reason)