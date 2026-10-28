from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from ....services.analytics.analytics_service import analytics_service


async def failure_breakdown(
    merchant_id: UUID,
    user_id: UUID,
    previous_start: date,
    previous_end: date,
    current_start: date,
    current_end: date
) -> dict:
    # Query both periods using the same database session.
    previous = await analytics_service.get_failures_by_category(
        user_id=user_id,
        merchant_id=merchant_id,
        start_date=previous_start,
        end_date=previous_end,
    )

    current = await analytics_service.get_failures_by_category(
        merchant_id=merchant_id,
        user_id=user_id,
        start_date=current_start,
        end_date=current_end,
    )

    # Include categories found in either period.
    categories = previous.keys() | current.keys()

    previous_total = sum(previous.values())
    current_total = sum(current.values())
    net_increase = current_total - previous_total

    breakdown = []

    for category in categories:
        previous_count = previous.get(category, 0)
        current_count = current.get(category, 0)
        change = current_count - previous_count

        # A zero net increase makes the contribution percentage
        # undefined, so return None in that case.
        if net_increase != 0:
            contribution = (
                Decimal(change)
                / Decimal(net_increase)
                * Decimal("100")
            ).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
        else:
            contribution = None

        breakdown.append(
            {
                "failure_category": category or "UNKNOWN",
                "previous_failures": previous_count,
                "current_failures": current_count,
                "change": change,
                "contribution_to_net_increase_pct": (
                    float(contribution)
                    if contribution is not None
                    else None
                ),
            }
        )

    # Show the biggest increases first.
    breakdown.sort(
        key=lambda item: item["change"],
        reverse=True,
    )

    return {
        "previous_total_failures": previous_total,
        "current_total_failures": current_total,
        "net_increase": net_increase,
        "failure_breakdown": breakdown,
        "interpretation": (
            "Contribution percentages represent each category's "
            "share of the net change in failed-payment counts. "
            "They do not establish causation."
        ),
    }