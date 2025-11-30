import uuid
from datetime import datetime
from pydantic import BaseModel

class DomainEvent(BaseModel):
    event_id: uuid.UUID = uuid.uuid4()
    occurred_on: datetime = datetime.now()

class ReservationCreated(DomainEvent):
    reservation_id: uuid.UUID
    customer_id: uuid.UUID
    start_time: datetime

class ReservationConfirmed(DomainEvent):
    reservation_id: uuid.UUID
    confirmed_by: str = "SYSTEM"

class ReservationCancelled(DomainEvent):
    reservation_id: uuid.UUID
    reason: str