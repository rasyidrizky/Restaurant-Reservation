from fastapi import FastAPI
from src.api.reservation_api import router as reservation_router

app = FastAPI()
app.include_router(reservation_router)

@app.get("/")
def root():
    return {"message": "Reservation API is running"}