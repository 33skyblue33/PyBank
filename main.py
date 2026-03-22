from fastapi import FastAPI
from app.routers import bnpl_router

app = FastAPI(
    title="PyBank API",
    description="System bankowy: BNPL + Fraud Detection + Rate Limiter",
    version="1.0.0"
)

app.include_router(bnpl_router.router)

@app.get("/")
def root():
    return {"message": "Witaj w PyBank API!", "status": "running"}