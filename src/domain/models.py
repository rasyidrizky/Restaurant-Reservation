import uuid
from datetime import datetime
from typing import List, Optional
from .value_objects import (
    ReservationStatus, ContactInfo, ReservationTime, 
    ReservationPolicy, CancellationReason
)

class TableAssignment:
    def __init__(self, table_id: uuid.UUID, capacity: int, area: str):
        self.assignment_id = uuid.uuid4()
        self.table_id = table_id
        self.capacity = capacity
        self.area = area

class ReservationHistory:
    def __init__(self, action: str, note: str = ""):
        self.history_id = uuid.uuid4()
        self.timestamp = datetime.now()
        self.action = action
        self.note = note

class Reservation:
    def __init__(
        self, 
        customer_id: uuid.UUID, 
        contact_info: ContactInfo, 
        reservation_time: ReservationTime,
        policy: ReservationPolicy
    ):
        self.reservation_id = uuid.uuid4()
        self.customer_id = customer_id
        self.contact_info = contact_info
        self.reservation_time = reservation_time
        self.policy = policy
        
        self.status = ReservationStatus.PENDING
        
        self.table_assignment: Optional[TableAssignment] = None
        self.history: List[ReservationHistory] = []
        
        self._record_history("CREATED", "Reservation created")

    def _record_history(self, action: str, note: str):
        log = ReservationHistory(action, note)
        self.history.append(log)

    def confirm_reservation(self):
        if self.status == ReservationStatus.CANCELLED:
            raise ValueError("Cannot confirm a cancelled reservation.")
        
        self.status = ReservationStatus.CONFIRMED
        self._record_history("CONFIRMED", "Reservation confirmed by system/staff")

    def cancel_reservation(self, reason: CancellationReason):
        if self.status == ReservationStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed reservation.")
            
        self.status = ReservationStatus.CANCELLED
        self._record_history("CANCELLED", f"{reason.reason_code}: {reason.description}")

    def assign_table(self, table_id: uuid.UUID, capacity: int, area: str):
        if self.status == ReservationStatus.CANCELLED:
            raise ValueError("Cannot assign table to cancelled reservation.")
            
        self.table_assignment = TableAssignment(table_id, capacity, area)
        self._record_history("TABLE_ASSIGNED", f"Assigned to Table ID {table_id} ({area})")