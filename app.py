import streamlit as st
from copy import deepcopy
from data import appointments, customers
from matching import rank_customers

st.set_page_config(
    page_title="SlotRescue AI",
    page_icon="📅",
    layout="wide"
)

if "appointments" not in st.session_state:
    st.session_state.appointments = deepcopy(appointments)

st.title("SlotRescue AI")
st.subheader("Intelligent Appointment Recovery Agent")

st.write("Helping businesses recover revenue from cancelled appointments.")

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

    if appointment["status"] == "Cancelled":

        st.subheader(
            f'{appointment["service"]} at {appointment["time"]}'
        )

        st.warning(
            f'Potential revenue loss: £{appointment["price"]}'
        )

        ranked = rank_customers(appointment, customers)

        if ranked:
            st.dataframe(ranked)
        else:
            st.error("No eligible customers found.")