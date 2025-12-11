from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.database import Base
import uuid

class ReservationORM(Base):
    __tablename__ = "reservations"

    reservation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String, default="PENDING")
    
    start_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=90)
    
    contact_name = Column(String, nullable=False)
    contact_phone = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    
    table_id = Column(UUID(as_uuid=True), nullable=True)
    table_area = Column(String, nullable=True)

    payment_status = Column(String, default="UNPAID")
    payment_amount = Column(Integer, default=0)