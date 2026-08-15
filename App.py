"""Automobile Spare Parts & Garage Billing System.

A Streamlit app backed by SQLite (garage_billing.db) that handles inventory,
billing, pending-payment tracking, WhatsApp sharing, and a sales dashboard.
"""

import pandas as pd
import streamlit as st

import db
from pages import inventory, billing, udhar

st.set_page_config(
    page_title="Garage Billing System",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialise the database once per session.
db.init_db()

def main() -> None:
    st.markdown(
        """
        <style>
        .main .block-container {max-width: 1200px; padding-top: 1.5rem;}
        .metric-card {
            background: #0f172a; border-radius: 12px; padding: 1.2rem 1.4rem;
            border: 1px solid #1e293b;
        }
        .big-metric {font-size: 2rem; font-weight: 700; line-height: 1.1;}
        .metric-label {font-size: .8rem; color: #94a3b8; text-transform: uppercase;
                       letter-spacing: .05em; margin-bottom: .3rem;}
        div[data-testid="stMetric"] {background: #111827; border: 1px solid #1f2937;
            border-radius: 10px; padding: .9rem 1rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("## 🔧 Garage Billing")
        st.caption("Spare Parts • Billing • Udhar Khata")
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📦 Inventory", "🧾 New Bill", "📒 Udhar Khata"],
            index=0,
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("Data saved locally in `garage_billing.db`")

    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📦 Inventory":
        inventory.show()
    elif page == "🧾 New Bill":
        billing.show()
    elif page == "📒 Udhar Khata":
        udhar.show()

def show_dashboard() -> None:
    st.title("📊 Sales Dashboard")

    m = db.get_dashboard_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"₹{m['total_revenue']:,.0f}")
    c2.metric("Cash Collected", f"₹{m['total_cash']:,.0f}")
    c3.metric("Pending Udhar", f"₹{m['total_pending']:,.0f}")
    c4.metric("Total Bills", f"{m['total_bills']:,}")

    st.divider()

    # Daily sales line chart
    daily = db.get_daily_sales()
    if daily:
        df = pd.DataFrame(daily)
        st.subheader("📈 Daily Sales History")
        st.line_chart(df.set_index("bill_date")[["total", "cash", "pending"]],
                     color=["#3b82f6", "#22c55e", "#ef4444"])
    else:
        st.info("No sales recorded yet — create your first bill to see charts here.")

    st.divider()

    # Top 5 best-selling parts
    top = db.get_top_parts(5)
    if top:
        st.subheader("🏆 Top 5 Best-Selling Parts")
        tdf = pd.DataFrame(top)
        tdf.columns = ["Part Name", "Qty Sold", "Revenue"]
        tdf["Revenue"] = tdf["Revenue"].map(lambda v: f"₹{v:,.0f}")
        st.dataframe(tdf, use_container_width=True, hide_index=True)
    else:
        st.info("No sales yet — top parts will appear here once bills are created.")

if __name__ == "__main__":
    main()
    
