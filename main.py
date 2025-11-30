from fastapi import FastAPI
import uvicorn
from src.api.routes import router as reservation_router

app = FastAPI(
    title="Restaurant Reservation System",
    description="API implementation for II3160 Teknologi Sistem Terintegrasi",
    version="1.0.0"
)

app.include_router(reservation_router, prefix="/api", tags=["Reservations"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)