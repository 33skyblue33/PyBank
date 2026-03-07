from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Literal

class BNPLRequest(BaseModel):
    purchase_amount : Decimal = Field(..., gt=0, description="Kwota zakupu")
    credit_score : int = Field(..., ge=300, le=850, description="Wynik kredytowy")
    preferred_installments : Literal[3,6,12] = Field(..., description="Preferowana liczba rat")
misiu = BNPLRequest(purchase_amount=1000, credit_score=750, preferred_installments=6)
print(misiu.model_dump_json(indent=2))