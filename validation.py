def validate_recommendation(recommendation, candidates):

    if not isinstance(recommendation, dict):
        return False

    required_fields = [
        "customer_id",
        "customer_name",
        "discount",
        "recovered_revenue",
        "reasoning",
        "offer_message"
    ]

    for field in required_fields:
        if field not in recommendation:
            return False

    for candidate in candidates:

        if candidate["id"] == recommendation["customer_id"]:

            return (
                candidate["name"] == recommendation["customer_name"]
                and candidate["discount"] == recommendation["discount"]
                and candidate["recovered_revenue"] == recommendation["recovered_revenue"]
                and isinstance(recommendation["reasoning"], str)
                and bool(recommendation["reasoning"].strip())
                and isinstance(recommendation["offer_message"], str)
                and bool(recommendation["offer_message"].strip())
            )

    return False


def fallback_recommendation(appointment, candidates):

    if not candidates:
        return None

    best = candidates[0]

    return {
        "customer_id": best["id"],
        "customer_name": best["name"],
        "discount": best["discount"],
        "recovered_revenue": best["recovered_revenue"],
        "reasoning": "Selected using deterministic revenue optimisation.",
        "offer_message": (
            f'Hi {best["name"]}! '
            f'A {appointment["service"]} appointment '
            f'is available at {appointment["time"]} '
            f'for £{best["recovered_revenue"]}. '
            f'Would you like to book it?'
        )
    }