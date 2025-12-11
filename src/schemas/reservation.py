from pydantic import BaseModel, UUID4, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from src.domain.value_objects import ContactInfo, ReservationStatus

class CustomerDetails(BaseModel):
    id: UUID4
    name: str
    phone: str
    email: EmailStr

class BookingInfo(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    is_peak_hour: bool = False 

class PaymentInfo(BaseModel):
    status: str
    amount: float
    currency: str = "IDR"

class Metadata(BaseModel):
    api_version: str = "v1"
    response_generated_at: datetime = Field(default_factory=datetime.now)

class ReservationResponse(BaseModel):
    reservation_id: UUID4
    status: ReservationStatus
    table_area: Optional[str] = None
    customer_details: CustomerDetails
    booking_info: BookingInfo
    payment_info: PaymentInfo
    meta: Metadata
    
class ContactInfoSchema(BaseModel):
    name: str
    phone: str
    email: EmailStr

class CreateReservationRequest(BaseModel):
    customer_id: UUID4
    contact_info: ContactInfoSchema
    start_time: datetime
    duration_minutes: int = 90

class AssignTableRequest(BaseModel):
    table_id: UUID4
    capacity: int
    area: str

class CancelRequest(BaseModel):
    reason_code: str
    description: str
    
class ReservationStats(BaseModel):
    total_reservations: int
    pending_count: int
    confirmed_count: int
    checked_in_count: int
    completed_count: int
    cancelled_count: int
    total_revenue: float
    generated_at: datetime = Field(default_factory=datetime.now)