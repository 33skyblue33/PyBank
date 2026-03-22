from fastapi import APIRouter, HTTPException
from app.models.bnpl import BNPLRequest, BNPLResponse

router = APIRouter(prefix="/api/bnpl", tags=["BNPL"])

@router.post("/calculate")
def calculate():
    return {"info": "Tu będzie logika BNPL"}