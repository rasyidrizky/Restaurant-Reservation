from uuid import uuid4
from datetime import datetime
from .value_objects import (
    ReservationTime, ReservationPolicy, ReservationStatus, PaymentDetail
)
from .table_assignment import TableAssignment
from .reservation_history import ReservationHistory

class Reservation:
    def __init__(self, customer_id: str, reservation_time: ReservationTime, policy: ReservationPolicy):
        self.reservation_id = str(uuid4())
        self.customer_id = customer_id
        self.reservation_time = reservation_time
        self.policy = policy
        self.status = ReservationStatus(status="PENDING")
        self.table: TableAssignment | None = None
        self.deposit: PaymentDetail | None = None
        self.history: list[ReservationHistory] = []

    def confirm(self):
        self.status.status = "CONFIRMED"
        self.history.append(
            ReservationHistory(
                timestamp=datetime.now(),
                action="CONFIRMED",
                note="Reservation confirmed."
            )
        )

    def assign_table(self, table: TableAssignment):
        self.table = table
        self.history.append(
            ReservationHistory(
                timestamp=datetime.now(),
                action="TABLE_ASSIGNED",
                note=f"Table {table.table_id} assigned."
            )
        )
