from decimal import Decimal


def calculate_payment_metrics(
    total: int,
    succeeded: int,
    failed: int,
) -> dict:
    if min(total, succeeded, failed) < 0:
        raise ValueError("Counts cannot be negative.")

    if succeeded + failed > total:
        raise ValueError("Outcome counts exceed total attempts.")

    if total == 0:
        return {
            "total": 0,
            "succeeded": succeeded,
            "failed": failed,
            "success_rate_pct": None,
            "failure_rate_pct": None,
        }

    success_rate = (
        Decimal(succeeded) / Decimal(total) * Decimal("100")
    )
    failure_rate = (
        Decimal(failed) / Decimal(total) * Decimal("100")
    )

    return {
        "total": total,
        "succeeded": succeeded,
        "failed": failed,
        "success_rate_pct": str(
            success_rate.quantize(Decimal("0.01"))
        ),
        "failure_rate_pct": str(
            failure_rate.quantize(Decimal("0.01"))
        ),
    }