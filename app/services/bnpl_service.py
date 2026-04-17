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


def check_frequency(
    transactions: list[Transaction],
    max_count: int = 3,
    window_seconds: int = 60,
) -> FraudAlert | None:
    sorted_txns = sorted(transactions, key=lambda t: t.timestamp)
    for i in range(len(sorted_txns)):
        window_end = sorted_txns[i].timestamp + timedelta(seconds=window_seconds)
        window_txns = [t for t in sorted_txns[i:] if t.timestamp <= window_end]
        if len(window_txns) > max_count:
            return FraudAlert(
                rule_name="Zbyt częste transakcje",
                description=f"Wykryto {len(window_txns)} transakcji w ciągu {window_seconds} sekund (limit: {max_count})",
                triggered_by=[t.transaction_id for t in window_txns],
            )
    return None

def check_amount_anomaly(
    transactions: list[Transaction],
    threshold: Decimal = Decimal("5.0"),
) -> FraudAlert | None:
    if len(transactions) < 2:
        return None
    amounts = [t.amount for t in transactions]
    avg = sum(amounts) / len(amounts)
    last = transactions[-1]
    if avg > 0 and last.amount > avg * threshold:
        return FraudAlert(
            rule_name="Anomalia kwoty",
            description=f"Transakcja na kwotę {last.amount} przekracza {threshold * 100}% średniej ({avg:.2f})",
            triggered_by=[last.transaction_id],
        )
    return None

def check_location(
    transactions: list[Transaction],
    max_minutes: int = 30,
) -> FraudAlert | None:
    sorted_txns = sorted(transactions, key=lambda t: t.timestamp)
    for i in range(1, len(sorted_txns)):
        prev, curr = sorted_txns[i - 1], sorted_txns[i]
        time_diff = (curr.timestamp - prev.timestamp).total_seconds() / 60
        if prev.country != curr.country and time_diff <= max_minutes:
            return FraudAlert(
                rule_name="Podejrzana lokalizacja",
                description=f"Transakcje z {prev.country} i {curr.country} w odstępie {time_diff:.0f} minut",
                triggered_by=[prev.transaction_id, curr.transaction_id],
            )
    return None

def check_fraud(transactions: list[Transaction]) -> FraudCheckResponse:
    alerts: list[FraudAlert] = []

    freq = check_frequency(transactions)
    if freq:
        alerts.append(freq)

    anomaly = check_amount_anomaly(transactions)
    if anomaly:
        alerts.append(anomaly)

    location = check_location(transactions)
    if location:
        alerts.append(location)

    risk_score = min(len(alerts) * 33, 100)
    blocked = len(alerts) >= 2

    return FraudCheckResponse(
        blocked=blocked,
        risk_score=risk_score,
        alerts=alerts,
    )
    