from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
import uuid
from datetime import timedelta
from typing import List, Optional

from src.infrastructure.database import get_db
from src.infrastructure.orm_models import ReservationORM
from src.schemas.reservation import (
    CreateReservationRequest, ReservationResponse, 
    AssignTableRequest, CancelRequest, ReservationStats
)
from src.core.security import get_current_user

router = APIRouter()

def map_to_response(orm_obj: ReservationORM) -> ReservationResponse:
    end_time = orm_obj.start_time + timedelta(minutes=orm_obj.duration_minutes)
    is_peak = True if orm_obj.start_time.hour >= 18 else False

    return ReservationResponse(
        reservation_id=orm_obj.reservation_id,
        status=orm_obj.status,
        table_area=orm_obj.table_area,
        
        customer_details={
            "id": orm_obj.customer_id,
            "name": orm_obj.contact_name,
            "phone": orm_obj.contact_phone,
            "email": orm_obj.contact_email
        },
        
        booking_info={
            "start_time": orm_obj.start_time,
            "end_time": end_time,
            "duration_minutes": orm_obj.duration_minutes,
            "is_peak_hour": is_peak
        },
        
        payment_info={
            "status": orm_obj.payment_status or "UNPAID",
            "amount": orm_obj.payment_amount or 0,
            "currency": "IDR"
        },
        
        meta={
            "api_version": "v1.0.5"
        }
    )

# --- CRUD ENDPOINTS ---

@router.post("/reservations", response_model=ReservationResponse)
def create_reservation(
    request: CreateReservationRequest, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    new_reservation = ReservationORM(
        reservation_id=uuid.uuid4(),
        customer_id=request.customer_id,
        status="PENDING",
        start_time=request.start_time,
        duration_minutes=request.duration_minutes,
        contact_name=request.contact_info.name,
        contact_phone=request.contact_info.phone,
        contact_email=request.contact_info.email,
        payment_status="UNPAID",
        payment_amount=0
    )
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    
    return map_to_response(new_reservation)

@router.get("/reservations", response_model=List[ReservationResponse])
def list_reservations(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    query = db.query(ReservationORM)
    if status:
        query = query.filter(ReservationORM.status == status)
    
    reservations = query.offset(skip).limit(limit).all()
    return [map_to_response(res) for res in reservations]

@router.get("/reservations/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: UUID, 
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    res = db.query(ReservationORM).filter(ReservationORM.reservation_id == reservation_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return map_to_response(res)

# --- BUSINESS FLOW ENDPOINTS ---

@router.post("/reservations/{reservation_id}/confirm")
def confirm_reservation(reservation_id: UUID, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    res = db.query(ReservationORM).filter(ReservationORM.reservation_id == reservation_id).first()
    if not res: raise HTTPException(status_code=404, detail="Reservation not found")
    if res.status == "CANCELLED": raise HTTPException(status_code=400, detail="Cannot confirm cancelled reservation.")
    
    res.status = "CONFIRMED"
    db.commit()
    return {"message": "Confirmed", "status": "CONFIRMED"}

@router.post("/reservations/{reservation_id}/check-in")
def check_in_customer(reservation_id: UUID, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    res = db.query(ReservationORM).filter(ReservationORM.reservation_id == reservation_id).first()
    if not res: raise HTTPException(status_code=404, detail="Reservation not found")
    if res.status != "CONFIRMED": raise HTTPException(status_code=400, detail="Reservation must be CONFIRMED to check-in.")
    
    res.status = "CHECKED_IN"
    db.commit()
    return {"message": "Checked-in", "status": "CHECKED_IN"}

@router.post("/reservations/{reservation_id}/complete")
def complete_reservation(reservation_id: UUID, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    res = db.query(ReservationORM).filter(ReservationORM.reservation_id == reservation_id).first()
    if not res: raise HTTPException(status_code=404, detail="Reservation not found")
    if res.status != "CHECKED_IN": raise HTTPException(status_code=400, detail="Customer must be CHECKED_IN to complete.")
    
    res.status = "COMPLETED"
    db.commit()
    return {"message": "Completed", "status": "COMPLETED"}

@router.post("/reservations/{reservation_id}/assign-table")
def assign_table(reservation_id: UUID, request: AssignTableRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    res = db.query(ReservationORM).filter(ReservationORM.reservation_id == reservation_id).first()
    if not res: raise HTTPException(status_code=404, detail="Reservation not found")
    if res.status == "CANCELLED": raise HTTPException(status_code=400, detail="Cannot assign table to cancelled reservation.")
    
    res.table_id = request.table_id
    res.table_area = request.area
    db.commit()
    return {"message": "Table assigned"}

@router.post("/reservations/{reservation_id}/cancel")
def cancel_reservation(reservation_id: UUID, request: CancelRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    res = db.query(ReservationORM).filter(ReservationORM.reservation_id == reservation_id).first()
    if not res: raise HTTPException(status_code=404, detail="Reservation not found")
    if res.status == "COMPLETED": raise HTTPException(status_code=400, detail="Cannot cancel completed reservation.")
    
    res.status = "CANCELLED"
    db.commit()
    return {"message": "Cancelled", "status": "CANCELLED"}

@router.get("/stats", response_model=ReservationStats)
def get_reservation_stats(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    stats_query = db.query(ReservationORM.status, func.count(ReservationORM.reservation_id)).group_by(ReservationORM.status).all()
    counts = dict(stats_query)
    total_revenue = db.query(func.sum(ReservationORM.payment_amount)).scalar() or 0.0
    
    return ReservationStats(
        total_reservations=sum(counts.values()),
        pending_count=counts.get("PENDING", 0),
        confirmed_count=counts.get("CONFIRMED", 0),
        checked_in_count=counts.get("CHECKED_IN", 0),
        completed_count=counts.get("COMPLETED", 0),
        cancelled_count=counts.get("CANCELLED", 0),
        total_revenue=total_revenue
    )