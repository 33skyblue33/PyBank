from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from app.models.bnpl import BNPLRequest, BNPLResponse, InstallmentPlan

def assess_risk(credit_score: int) -> str:
    if credit_score >= 700:
        return "low"
    elif credit_score > 600:
        return "medium"
    elif credit_score <= 500:
        return "high"
    else:
        return "rejected"

def calculate_interest_rate(risk_level: str) -> Decimal:
    rates = {
        "low": Decimal("0"),
        "medium": Decimal("5.99"),
        "high": Decimal("15.99"),
        "rejected": Decimal("-1"),
    }
    return rates.get(risk_level, Decimal("-1"))

def generate_installment_plan(
    total: Decimal, num_installments: int, start_date: date
) -> list[InstallmentPlan]:
    monthly = (total / num_installments).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    installments = []
    for i in range(1, num_installments + 1):
        due = start_date + timedelta(days=30 * i)
        if i < num_installments:
            amount = monthly
        else:
            amount = total - monthly * (num_installments - 1)
        installments.append(
            InstallmentPlan(installment_number=i, amount=amount, due_date=due)
        )
    return installments

def process_bnpl_request(request: BNPLRequest) -> BNPLResponse:
    risk = assess_risk(request.credit_score)
    rate = calculate_interest_rate(risk)
    if rate < 0 :
        return BNPLResponse(approved=False, interest_rate=rate, monthly_payment=0, total_cost=0, installments=[])
    interest = request.purchase_amount * rate / 100
    total = request.purchase_amount + interest
    monthly = total / request.preferred_installments
    installments = generate_installment_plan(total, request.preferred_installments, date.today())
    return BNPLResponse(approved=True, interest_rate=rate, monthly_payment=monthly.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), total_cost=total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), installments=installments)


