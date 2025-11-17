from datetime import datetime
from pydantic import BaseModel

class ReservationHistory(BaseModel):
    timestamp: datetime
    action: str
    note: str
