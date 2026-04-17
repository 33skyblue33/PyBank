from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Literal
from datetime import date
from typing import Literal, List

class BNPLRequest(BaseModel):
    purchase_amount : Decimal = Field(gt=0, description="Kwota zakupu w PLN")
    credit_score : int = Field(ge=300, le=850, description="Ocena kredytowa klienta")
    preferred_installments : Literal[3,6,12] = Field(description="Preferowana liczba rat: 3, 6 lub 12")
request = BNPLRequest(purchase_amount=1000, credit_score=750, preferred_installments=6)

@field_validator("preferred_installments")
@classmethod
def validate_installments(cls, v):
    if v not in (3, 6, 12):
        raise ValueError("Liczba rat musi wynosić 3, 6 lub 12")
    return v

class BNPLInstallmentPlan(BaseModel):
    installment_number : int = Field(..., ge=1,description="Liczba rat")
    amount : Decimal = Field(..., gt=0, description="Kwota raty")
    due_data: date = Field(..., description="Data płatności")
plan = BNPLInstallmentPlan(installment_number=1, amount=100, due_data=date(2026, 1, 1))

class BNPLResponse(BaseModel):
    approved : bool = Field(..., description="Does approved credit")
    interest_rate : Decimal = Field(..., ge=0, le=100, description="Interest rate")
    monthly_payment : Decimal = Field(..., gt=0, description="Monthly payment")
    total_cost : Decimal = Field(..., gt=0, description="Total cost")
    installments : List[BNPLInstallmentPlan] = Field(..., description="Installment plan")
response = BNPLResponse(approved=True, interest_rate=10, monthly_payment=100, total_cost=1000, installments=[plan])




print(request.model_dump_json(indent=2))
print(plan.model_dump_json(indent=2))
print(response.model_dump_json(indent=2))

