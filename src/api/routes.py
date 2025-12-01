from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from uuid import UUID

from src.domain.models import Reservation
from src.domain.value_objects import ReservationTime, ContactInfo, ReservationPolicy, CancellationReason
from src.schemas.reservation import (
    CreateReservationRequest, ReservationResponse, 
    AssignTableRequest, CancelRequest
)
from src.core.security import get_current_user

router = APIRouter()

reservation_db: Dict[UUID, Reservation] = {}

@router.post("/reservations", response_model=ReservationResponse)
def create_reservation(request: CreateReservationRequest, current_user: str = Depends(get_current_user)):
    time_vo = ReservationTime(
        start_time=request.start_time, 
        duration_minutes=request.duration_minutes
    )
    policy_vo = ReservationPolicy()

    new_reservation = Reservation(
        customer_id=request.customer_id,
        contact_info=request.contact_info,
        reservation_time=time_vo,
        policy=policy_vo
    )

    reservation_db[new_reservation.reservation_id] = new_reservation

    return map_to_response(new_reservation)

@router.get("/reservations/{reservation_id}", response_model=ReservationResponse)
def get_reservation(reservation_id: UUID, current_user: str = Depends(get_current_user)):
    if reservation_id not in reservation_db:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    reservation = reservation_db[reservation_id]
    return map_to_response(reservation)

@router.post("/reservations/{reservation_id}/confirm")
def confirm_reservation(reservation_id: UUID, current_user: str = Depends(get_current_user)):
    if reservation_id not in reservation_db:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    reservation = reservation_db[reservation_id]
    
    try:
        reservation.confirm_reservation() 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"message": "Reservation confirmed", "status": reservation.status}

@router.post("/reservations/{reservation_id}/assign-table")
def assign_table(reservation_id: UUID, request: AssignTableRequest, current_user: str = Depends(get_current_user)):
    if reservation_id not in reservation_db:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    reservation = reservation_db[reservation_id]
    
    try:
        reservation.assign_table(request.table_id, request.capacity, request.area)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"message": "Table assigned successfully"}

@router.post("/reservations/{reservation_id}/cancel")
def cancel_reservation(reservation_id: UUID, request: CancelRequest, current_user: str = Depends(get_current_user)):
    if reservation_id not in reservation_db:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    reservation = reservation_db[reservation_id]
    reason_vo = CancellationReason(reason_code=request.reason_code, description=request.description)
    
    try:
        reservation.cancel_reservation(reason_vo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"message": "Reservation cancelled", "status": reservation.status}

def map_to_response(res: Reservation) -> ReservationResponse:
    area = res.table_assignment.area if res.table_assignment else None
    return ReservationResponse(
        reservation_id=res.reservation_id,
        customer_id=res.customer_id,
        status=res.status,
        start_time=res.reservation_time.start_time,
        end_time=res.reservation_time.end_time,
        contact_name=res.contact_info.name,
        table_area=area
    )