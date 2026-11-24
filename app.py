import streamlit as st
from copy import deepcopy
from datetime import datetime
from data import appointments, customers
from matching import rank_customers
from agent import safe_recommendation
from analytics import calculate_metrics
from validation import validate_recommendation

st.set_page_config(
    page_title="SlotRescue AI",
    page_icon="📅",
    layout="wide"
)

# Session state

defaults = {
    "appointments": deepcopy(appointments),
    "recommendations": {},
    "used_customers": [],
    "rejected_customers": {},
    "activity_log": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def log_activity(action, details):
    st.session_state.activity_log.append({
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Action": action,
        "Details": details
    })


# Sidebar

with st.sidebar:
    st.title("SlotRescue AI")
    st.caption("INTELLIGENT APPOINTMENT RECOVERY")

    st.divider()

    st.success("Recovery agent ready")

    st.markdown("### Technology")
    st.write("Nebius Token Factory")
    st.write("Python · Streamlit")

    st.markdown("### Safety controls")
    st.write("✓ Customer eligibility checks")
    st.write("✓ AI response validation")
    st.write("✓ Automatic fallback")
    st.write("✓ Human approval")

    st.divider()

    st.info("Simulation mode. All data is fictional.")

    if st.button("Reset Simulation", use_container_width=True):
        for key, value in defaults.items():
            st.session_state[key] = deepcopy(value)
        st.rerun()


# Main heading

st.title("SlotRescue AI")

st.markdown(
    "### Turn cancelled appointments into recovered revenue."
)

st.caption(
    "AI-powered appointment recovery for beauty and wellness businesses."
)

metrics = calculate_metrics(st.session_state.appointments)

available_customers = [
    c for c in customers
    if c["id"] not in st.session_state.used_customers
]

overview, recovery, waiting_list, activity = st.tabs([
    "📊 Business Overview",
    "🤖 Recovery Agent",
    "👥 Customer Waiting List",
    "📋 Activity Log"
])


# Business overview

with overview:

    st.subheader("Business Performance")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Revenue Recovered",
        f'£{metrics["revenue_recovered"]}',
        border=True
    )

    c2.metric(
        "Revenue at Risk",
        f'£{metrics["revenue_at_risk"]}',
        border=True
    )

    c3.metric(
        "Recovery Rate",
        f'{metrics["recovery_rate"]:.1f}%',
        border=True
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "Total Appointments",
        metrics["total_appointments"],
        border=True
    )

    c5.metric(
        "Recovered Appointments",
        metrics["recovered_appointments"],
        border=True
    )

    c6.metric(
        "Total Discounts",
        f'£{metrics["total_discounts"]}',
        border=True
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Revenue Performance")

        st.bar_chart({
            "Recovered": [metrics["revenue_recovered"]],
            "At Risk": [metrics["revenue_at_risk"]]
        })

    with right:
        st.subheader("Recovery Progress")

        st.progress(metrics["recovery_rate"] / 100)

        st.write(
            f'{metrics["recovered_appointments"]} of '
            f'{metrics["total_cancellations"]} '
            'cancelled appointments recovered.'
        )

        st.metric(
            "Available Customers",
            len(available_customers)
        )

    st.divider()

    st.subheader("Appointment Schedule")

    st.dataframe(
        st.session_state.appointments,
        hide_index=True,
        use_container_width=True
    )


# Recovery agent

with recovery:

    st.subheader("Appointment Recovery Agent")

    st.write(
        "Simulate a cancellation and let the AI agent "
        "identify a suitable replacement customer."
    )

    booked = [
        a for a in st.session_state.appointments
        if a["status"] == "Booked"
    ]

    with st.container(border=True):

        st.markdown("#### Simulate a cancellation")

        if booked:

            selected_id = st.selectbox(
                "Select appointment",
                [a["id"] for a in booked],
                format_func=lambda appointment_id: next(
                    f'{a["service"]} | {a["time"]} | £{a["price"]}'
                    for a in booked
                    if a["id"] == appointment_id
                )
            )

            if st.button(
                "Cancel Appointment",
                use_container_width=True
            ):

                for a in st.session_state.appointments:

                    if a["id"] == selected_id:

                        a["status"] = "Cancelled"

                        log_activity(
                            "Appointment Cancelled",
                            f'{a["service"]} at {a["time"]} '
                            f'— £{a["price"]} at risk'
                        )

                        break

                st.rerun()

        else:
            st.info("No booked appointments remaining.")

    st.subheader("Recovery Opportunities")

    cancelled = [
        a for a in st.session_state.appointments
        if a["status"] == "Cancelled"
    ]

    if not cancelled:
        st.success("No outstanding cancellations.")

    for appointment in cancelled:

        appointment_id = appointment["id"]

        rejected = st.session_state.rejected_customers.get(
            appointment_id, []
        )

        eligible_pool = [
            c for c in available_customers
            if c["id"] not in rejected
        ]

        ranked = rank_customers(
            appointment, eligible_pool
        )

        with st.container(border=True):

            st.markdown(
                f'### {appointment["service"]} '
                f'— {appointment["time"]}'
            )

            st.warning(
                f'£{appointment["price"]} revenue at risk'
            )

            st.caption(
                f'{len(ranked)} eligible replacement customers'
            )

            if not ranked:
                st.error(
                    "No remaining eligible customers "
                    "for this appointment."
                )
                continue

            with st.expander("View ranked candidates"):
                st.dataframe(
                    ranked,
                    hide_index=True,
                    use_container_width=True
                )

            if st.button(
                "Generate AI Recommendation",
                key=f"generate_{appointment_id}",
                type="primary",
                use_container_width=True
            ):

                with st.spinner(
                    "Agent evaluating recovery options..."
                ):

                    result = safe_recommendation(
                        appointment, ranked
                    )

                    st.session_state.recommendations[
                        appointment_id
                    ] = result

                    if result:
                        log_activity(
                            "Recommendation Generated",
                            f'{result["customer_name"]} '
                            f'— {result["source"]}'
                        )

            recommendation = (
                st.session_state.recommendations.get(
                    appointment_id
                )
            )

            if not recommendation:
                continue

            if not validate_recommendation(
                recommendation, ranked
            ):
                st.session_state.recommendations.pop(
                    appointment_id, None
                )
                st.rerun()

            if recommendation["source"] == "Nebius AI":
                st.success("Validated Nebius AI recommendation")
            else:
                st.warning("Using validated rule-based fallback")

            st.markdown(
                f'### Recommended: '
                f'{recommendation["customer_name"]}'
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Original Price",
                f'£{appointment["price"]}',
                border=True
            )

            c2.metric(
                "Discount",
                f'£{recommendation["discount"]}',
                border=True
            )

            c3.metric(
                "Recovered Revenue",
                f'£{recommendation["recovered_revenue"]}',
                border=True
            )

            st.markdown("**Agent Decision**")
            st.write(recommendation["reasoning"])

            st.markdown("**Personalised Customer Offer**")
            st.info(recommendation["offer_message"])

            st.caption(
                "Human approval required. No real messages "
                "or bookings will be created."
            )

            approve, reject = st.columns(2)

            if approve.button(
                "Approve and Rebook",
                key=f"approve_{appointment_id}",
                type="primary",
                use_container_width=True
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

                appointment["recovery_source"] = (
                    recommendation["source"]
                )

                st.session_state.used_customers.append(
                    recommendation["customer_id"]
                )

                log_activity(
                    "Appointment Recovered",
                    f'{recommendation["customer_name"]} '
                    f'— £{recommendation["recovered_revenue"]}'
                )

                st.session_state.recommendations.pop(
                    appointment_id, None
                )

                st.rerun()

            if reject.button(
                "Reject Recommendation",
                key=f"reject_{appointment_id}",
                use_container_width=True
            ):

                st.session_state.rejected_customers.setdefault(
                    appointment_id, []
                ).append(recommendation["customer_id"])

                log_activity(
                    "Recommendation Rejected",
                    recommendation["customer_name"]
                )

                st.session_state.recommendations.pop(
                    appointment_id, None
                )

                st.rerun()


# Customer waiting list

with waiting_list:

    st.subheader("Customer Waiting List")

    c1, c2 = st.columns(2)

    c1.metric(
        "Available Customers",
        len(available_customers),
        border=True
    )

    c2.metric(
        "Customers Rebooked",
        len(st.session_state.used_customers),
        border=True
    )

    services = sorted({
        c["service"] for c in customers
    })

    selected_service = st.selectbox(
        "Filter by service",
        ["All Services"] + services
    )

    filtered = [
        c for c in available_customers
        if selected_service == "All Services"
        or c["service"] == selected_service
    ]

    st.dataframe(
        filtered,
        hide_index=True,
        use_container_width=True
    )


# Activity log

with activity:

    st.subheader("Agent Activity Log")

    st.write(
        "A transparent record of agent decisions "
        "and human approval actions."
    )

    if st.session_state.activity_log:

        st.dataframe(
            list(reversed(st.session_state.activity_log)),
            hide_index=True,
            use_container_width=True
        )

    else:
        st.info("No activity recorded yet.")


st.divider()

st.caption(
    "SlotRescue AI | Retail AI & Agents Hackathon 2026 | "
    "Powered by Nebius Token Factory | Simulation prototype"
)