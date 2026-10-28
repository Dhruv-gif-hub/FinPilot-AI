from decimal import Decimal


def compare_rates(
    previous_rate: str,
    current_rate: str,
) -> dict:
    previous = Decimal(previous_rate)
    current = Decimal(current_rate)

    difference = current - previous

    if previous == 0:
        relative_change_pct = None
    else:
        relative_change_pct = (
            difference / previous * Decimal("100")
        )

    return {
        "previous_rate_pct": str(previous),
        "current_rate_pct": str(current),
        "change_percentage_points": str(difference),
        "relative_change_pct": (
            str(relative_change_pct)
            if relative_change_pct is not None
            else None
        ),
    }