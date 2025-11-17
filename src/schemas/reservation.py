from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, List
from src.domain.value_objects import ContactInfo, ReservationStatus

class CreateReservationRequest(BaseModel):
    customer_id: UUID4
    contact_info: ContactInfo
    start_time: datetime
    duration_minutes: int = 90

class AssignTableRequest(BaseModel):
    table_id: UUID4
    capacity: int
    area: str

class CancelRequest(BaseModel):
    reason_code: str
    description: str

class TableAssignmentDTO(BaseModel):
    table_id: UUID4
    area: str

class ReservationResponse(BaseModel):
    reservation_id: UUID4
    customer_id: UUID4
    status: ReservationStatus
    start_time: datetime
    end_time: datetime
    contact_name: str
    table_area: Optional[str] = None