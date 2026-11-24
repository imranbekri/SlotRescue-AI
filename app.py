import streamlit as st
from data import appointments, customers

st.set_page_config(
    page_title="SlotRescue AI",
    page_icon="📅",
    layout="wide"
)

st.title("SlotRescue AI")
st.subheader("Intelligent Appointment Recovery Agent")

st.write("Helping businesses recover revenue from cancelled appointments.")

st.header("Appointment Dashboard")
st.dataframe(appointments)

st.header("Customer Waiting List")
st.dataframe(customers)