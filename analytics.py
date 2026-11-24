def calculate_metrics(appointments):

    cancelled = [
        a for a in appointments
        if a["status"] == "Cancelled"
    ]

    recovered = [
        a for a in appointments
        if a["status"] == "Recovered"
    ]

    total_cancellations = len(cancelled) + len(recovered)

    revenue_recovered = sum(
        a.get("recovered_revenue", 0)
        for a in recovered
    )

    revenue_at_risk = sum(
        a["price"] for a in cancelled
    )

    total_discounts = sum(
        a.get("discount", 0)
        for a in recovered
    )

    recovery_rate = (
        len(recovered) / total_cancellations * 100
        if total_cancellations else 0
    )

    return {
        "total_appointments": len(appointments),
        "total_cancellations": total_cancellations,
        "recovered_appointments": len(recovered),
        "revenue_recovered": revenue_recovered,
        "revenue_at_risk": revenue_at_risk,
        "total_discounts": total_discounts,
        "recovery_rate": recovery_rate
    }