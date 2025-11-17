from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel

from src.app.reservation_service import ReservationService
from src.infrastructure.reservation_repository import ReservationRepository
from src.domain.value_objects import ReservationTime

router = APIRouter()

repo = ReservationRepository()
service = ReservationService(repo)

class CreateReservationReq(BaseModel):
    customer_id: str
    start_time: datetime
    end_time: datetime

@router.post("/reservations")
def create_reservation(req: CreateReservationReq):
    time = ReservationTime(start_time=req.start_time, end_time=req.end_time)
    res = service.create_reservation(req.customer_id, time)
    return {"id": res.reservation_id, "status": res.status.status}

@router.post("/reservations/{reservation_id}/confirm")
def confirm_reservation(reservation_id: str):
    res = service.confirm_reservation(reservation_id)
    return {"status": res.status.status}
