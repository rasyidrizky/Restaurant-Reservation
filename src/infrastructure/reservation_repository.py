class ReservationRepository:
    def __init__(self):
        self._db = {}

    def save(self, reservation):
        self._db[reservation.reservation_id] = reservation
        return reservation

    def get(self, reservation_id: str):
        return self._db.get(reservation_id)
