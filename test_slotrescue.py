from copy import deepcopy
from unittest.mock import patch

from data import appointments, customers
from matching import rank_customers
from validation import validate_recommendation
from validation import fallback_recommendation
from analytics import calculate_metrics
from agent import safe_recommendation


def test_dataset_size():
    assert len(appointments) == 10
    assert len(customers) == 20


def test_revenue_optimisation():
    ranked = rank_customers(appointments[1], customers)
    assert ranked[0]["name"] == "Sophia"
    assert ranked[0]["recovered_revenue"] == 60


def test_waiting_time_priority():
    ranked = rank_customers(appointments[0], customers)
    assert ranked[0]["name"] == "Leo"


def test_service_matching():
    ranked = rank_customers(appointments[1], customers)
    assert all(c["service"] == "Massage" for c in ranked)


def test_time_matching():
    ranked = rank_customers(appointments[1], customers)
    assert all(c["available"] == "17:00" for c in ranked)


def test_duration_matching():
    ranked = rank_customers(appointments[6], customers)
    assert "Liam" not in [c["name"] for c in ranked]


def test_discount_calculation():
    ranked = rank_customers(appointments[3], customers)
    assert ranked[0]["discount"] == 5
    assert ranked[0]["recovered_revenue"] == 50


def test_no_eligible_customers():
    ranked = rank_customers(appointments[9], customers)
    assert ranked == []


def test_valid_recommendation():
    ranked = rank_customers(appointments[1], customers)
    result = fallback_recommendation(appointments[1], ranked)
    assert validate_recommendation(result, ranked)


def test_invalid_customer():
    ranked = rank_customers(appointments[1], customers)
    result = fallback_recommendation(appointments[1], ranked)
    result["customer_id"] = 999
    assert not validate_recommendation(result, ranked)


def test_invalid_discount():
    ranked = rank_customers(appointments[1], customers)
    result = fallback_recommendation(appointments[1], ranked)
    result["discount"] = 100
    assert not validate_recommendation(result, ranked)


def test_automatic_fallback():
    ranked = rank_customers(appointments[1], customers)

    with patch(
        "agent.generate_recommendation",
        side_effect=ValueError("Simulated API failure")
    ):
        result = safe_recommendation(appointments[1], ranked)

    assert result["source"] == "Rule-based fallback"
    assert result["customer_name"] == "Sophia"


def test_initial_analytics():
    metrics = calculate_metrics(appointments)
    assert metrics["total_appointments"] == 10
    assert metrics["revenue_recovered"] == 0
    assert metrics["recovery_rate"] == 0


def test_cancelled_appointment_analytics():
    simulated = deepcopy(appointments)
    simulated[1]["status"] = "Cancelled"

    metrics = calculate_metrics(simulated)

    assert metrics["revenue_at_risk"] == 60
    assert metrics["total_cancellations"] == 1


def test_recovered_appointment_analytics():
    simulated = deepcopy(appointments)

    simulated[1]["status"] = "Recovered"
    simulated[1]["recovered_revenue"] = 60
    simulated[1]["discount"] = 0

    metrics = calculate_metrics(simulated)

    assert metrics["revenue_recovered"] == 60
    assert metrics["revenue_at_risk"] == 0
    assert metrics["recovery_rate"] == 100