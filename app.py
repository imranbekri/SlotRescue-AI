import streamlit as st
from copy import deepcopy
from data import appointments, customers
from matching import rank_customers
from agent import safe_recommendation

st.set_page_config(
    page_title="SlotRescue AI",
    page_icon="📅",
    layout="wide"
)

if "appointments" not in st.session_state:
    st.session_state.appointments = deepcopy(appointments)

if "recommendations" not in st.session_state:
    st.session_state.recommendations = {}

if "used_customers" not in st.session_state:
    st.session_state.used_customers = []

st.title("SlotRescue AI")
st.subheader("Intelligent Appointment Recovery Agent")

st.write(
    "Helping businesses recover revenue from cancelled appointments."
)

st.header("Appointment Dashboard")
st.dataframe(st.session_state.appointments)

st.header("Customer Waiting List")
st.dataframe(customers)

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
                break

        st.rerun()

else:
    st.info("No booked appointments remaining.")

st.header("Recovery Opportunities")

for appointment in st.session_state.appointments:

    if appointment["status"] != "Cancelled":
        continue

    appointment_id = appointment["id"]

    st.subheader(
        f'{appointment["service"]} at {appointment["time"]}'
    )

    st.warning(
        f'Potential revenue loss: £{appointment["price"]}'
    )

    available_customers = [
        customer for customer in customers
        if customer["id"] not in st.session_state.used_customers
    ]

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

            st.session_state.recommendations.pop(
                appointment_id, None
            )

            st.rerun()

        if reject.button(
            "Reject Recommendation",
            key=f"reject_{appointment_id}"
        ):
            st.session_state.recommendations.pop(
                appointment_id, None
            )

            st.rerun()