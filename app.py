import streamlit as st
from copy import deepcopy
from datetime import datetime
from data import appointments, customers
from matching import rank_customers
from agent import safe_recommendation
from analytics import calculate_metrics

st.set_page_config(
    page_title="SlotRescue AI",
    page_icon="📅",
    layout="wide"
)

# Initialise session state

if "appointments" not in st.session_state:
    st.session_state.appointments = deepcopy(appointments)

if "recommendations" not in st.session_state:
    st.session_state.recommendations = {}

if "used_customers" not in st.session_state:
    st.session_state.used_customers = []

if "activity_log" not in st.session_state:
    st.session_state.activity_log = []


def log_activity(action, details):
    st.session_state.activity_log.append({
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Action": action,
        "Details": details
    })


# Sidebar

st.sidebar.title("SlotRescue AI")
st.sidebar.caption("Powered by Nebius Token Factory")
st.sidebar.info("Simulation mode — fictional business data")

if st.sidebar.button("Reset Simulation"):
    st.session_state.appointments = deepcopy(appointments)
    st.session_state.recommendations = {}
    st.session_state.used_customers = []
    st.session_state.activity_log = []
    st.rerun()


# Main dashboard

st.title("SlotRescue AI")
st.subheader("Intelligent Appointment Recovery Agent")

st.write(
    "Helping businesses recover revenue from cancelled appointments."
)

st.header("Business Performance")

metrics = calculate_metrics(
    st.session_state.appointments
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Appointments",
    metrics["total_appointments"]
)

col2.metric(
    "Recovered Appointments",
    metrics["recovered_appointments"]
)

col3.metric(
    "Revenue Recovered",
    f'£{metrics["revenue_recovered"]}'
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Revenue at Risk",
    f'£{metrics["revenue_at_risk"]}'
)

col5.metric(
    "Recovery Success Rate",
    f'{metrics["recovery_rate"]:.1f}%'
)

col6.metric(
    "Total Discounts",
    f'£{metrics["total_discounts"]}'
)

st.subheader("Revenue Performance")

st.bar_chart({
    "Recovered": [metrics["revenue_recovered"]],
    "At Risk": [metrics["revenue_at_risk"]]
})

st.divider()


# Appointment dashboard

st.header("Appointment Dashboard")
st.dataframe(st.session_state.appointments)

available_customers = [
    customer for customer in customers
    if customer["id"] not in st.session_state.used_customers
]

st.header("Customer Waiting List")

st.caption(
    f"{len(available_customers)} customers available"
)

st.dataframe(available_customers)


# Appointment cancellation

st.header("Simulate Appointment Cancellation")

booked = [
    appointment
    for appointment in st.session_state.appointments
    if appointment["status"] == "Booked"
]

if booked:

    selected = st.selectbox(
        "Select an appointment to cancel",
        booked,
        format_func=lambda a: (
            f'{a["service"]} - {a["time"]} - £{a["price"]}'
        )
    )

    if st.button("Cancel Appointment"):

        for appointment in st.session_state.appointments:

            if appointment["id"] == selected["id"]:

                appointment["status"] = "Cancelled"

                log_activity(
                    "Appointment Cancelled",
                    f'{appointment["service"]} at '
                    f'{appointment["time"]} — '
                    f'£{appointment["price"]} at risk'
                )

                break

        st.rerun()

else:
    st.info("No booked appointments remaining.")

st.divider()


# Recovery opportunities

st.header("Recovery Opportunities")

cancelled = [
    appointment
    for appointment in st.session_state.appointments
    if appointment["status"] == "Cancelled"
]

if not cancelled:
    st.info("No outstanding cancellations.")

for appointment in cancelled:

    appointment_id = appointment["id"]

    st.subheader(
        f'{appointment["service"]} at {appointment["time"]}'
    )

    st.warning(
        f'Potential revenue loss: £{appointment["price"]}'
    )

    ranked = rank_customers(
        appointment, available_customers
    )

    if not ranked:
        st.error("No eligible customers found.")
        continue

    st.dataframe(ranked)

    if st.button(
        "Generate AI Recommendation",
        key=f"generate_{appointment_id}"
    ):

        with st.spinner("AI agent analysing customers..."):

            recommendation = safe_recommendation(
                appointment, ranked
            )

            st.session_state.recommendations[
                appointment_id
            ] = recommendation

            if recommendation:
                log_activity(
                    "Recommendation Generated",
                    f'{recommendation["customer_name"]} '
                    f'— {recommendation["source"]}'
                )

    recommendation = st.session_state.recommendations.get(
        appointment_id
    )

    if recommendation:

        if recommendation["customer_id"] not in [
            customer["id"] for customer in ranked
        ]:

            st.session_state.recommendations.pop(
                appointment_id, None
            )

            st.rerun()

        st.success("Recovery recommendation generated")

        st.caption(
            f'Source: {recommendation["source"]}'
        )

        st.subheader(
            recommendation["customer_name"]
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Original Price",
            f'£{appointment["price"]}'
        )

        col2.metric(
            "Discount",
            f'£{recommendation["discount"]}'
        )

        col3.metric(
            "Recovered Revenue",
            f'£{recommendation["recovered_revenue"]}'
        )

        st.markdown("**Decision Explanation**")
        st.write(recommendation["reasoning"])

        st.markdown("**Personalised Customer Offer**")
        st.info(recommendation["offer_message"])

        approve, reject = st.columns(2)

        if approve.button(
            "Approve and Rebook",
            key=f"approve_{appointment_id}"
        ):

            appointment["status"] = "Recovered"

            appointment["replacement_customer"] = (
                recommendation["customer_name"]
            )

            appointment["recovered_revenue"] = (
                recommendation["recovered_revenue"]
            )

            appointment["discount"] = (
                recommendation["discount"]
            )

            st.session_state.used_customers.append(
                recommendation["customer_id"]
            )

            log_activity(
                "Appointment Recovered",
                f'{recommendation["customer_name"]} — '
                f'£{recommendation["recovered_revenue"]} recovered'
            )

            st.session_state.recommendations.pop(
                appointment_id, None
            )

            st.rerun()

        if reject.button(
            "Reject Recommendation",
            key=f"reject_{appointment_id}"
        ):

            log_activity(
                "Recommendation Rejected",
                recommendation["customer_name"]
            )

            st.session_state.recommendations.pop(
                appointment_id, None
            )

            st.rerun()

    st.divider()


# Activity log

st.header("Agent Activity Log")

if st.session_state.activity_log:

    st.dataframe(
        list(reversed(st.session_state.activity_log))
    )

else:
    st.info("No activity recorded yet.")