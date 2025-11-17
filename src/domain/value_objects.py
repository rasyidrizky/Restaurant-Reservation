from datetime import datetime
from pydantic import BaseModel

class ReservationTime(BaseModel):
    start_time: datetime
    end_time: datetime

class ReservationPolicy(BaseModel):
    max_duration: int
    cancel_deadline: datetime
    deposit_required: bool

class ReservationStatus(BaseModel):
    status: str

class PaymentDetail(BaseModel):
    amount: float
    method: str
    status: str
