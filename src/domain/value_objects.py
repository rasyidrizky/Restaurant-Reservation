from uuid import UUID
from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional

class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"

class ContactInfo(BaseModel):
    name: str
    phone: str
    email: EmailStr

class ReservationTime(BaseModel):
    start_time: datetime
    duration_minutes: int = 90

    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(minutes=self.duration_minutes)

class CancellationReason(BaseModel):
    reason_code: str
    description: str

class ReservationPolicy(BaseModel):
    deposit_required: bool = False
    auto_cancel_minutes: int = 15
    
class PaymentDetail(BaseModel):
    payment_id: Optional[UUID] = None
    amount: float = 0.0
    status: str = "UNPAID"
    method: Optional[str] = None