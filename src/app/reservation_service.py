from src.domain.reservation import Reservation
from src.domain.value_objects import ReservationTime, ReservationPolicy
from src.infrastructure.reservation_repository import ReservationRepository

class ReservationService:
    def __init__(self, repo: ReservationRepository):
        self.repo = repo

    def create_reservation(self, customer_id: str, time: ReservationTime):
        policy = ReservationPolicy(
            max_duration=120,
            cancel_deadline=time.start_time,
            deposit_required=False
        )

        reservation = Reservation(customer_id, time, policy)
        return self.repo.save(reservation)

    def confirm_reservation(self, reservation_id: str):
        reservation = self.repo.get(reservation_id)
        if reservation:
            reservation.confirm()
            return self.repo.save(reservation)
        return None
