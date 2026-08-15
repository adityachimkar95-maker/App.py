import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Pro Garage ERP", layout="wide", page_icon="🏎️")

# --- DATABASE SETUP ---
conn = sqlite3.connect("garage_billing_final.db", check_same_thread=False)
c = conn.cursor()

# Tables Setup
c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, mrp REAL, selling_price REAL, stock INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS mechanics (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS garage_profile (id INTEGER PRIMARY KEY DEFAULT 1, name TEXT, address TEXT, phone TEXT, tagline TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS bills (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, vehicle TEXT, labor_charge REAL, parts_total REAL, final_total REAL, paid REAL, udhar REAL, payment_mode TEXT, date TEXT, mechanic TEXT, work_details TEXT)''')
conn.commit()

# --- PREMIUM UI ---
st.markdown("""
<style>
    .stApp { background: #0f172a; color: #f8fafc; }
    .header-card { background: #1e293b; padding: 15px; border-radius: 12px; border-left: 6px solid #fbbf24; margin-bottom: 20px; }
    h1 { color: #fbbf24 !important; }
    .stButton>button { background: linear-gradient(135deg, #f59e0b, #d97706); color: #0f172a; font-weight: bold; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-card"><h1>🏎️ AUTO SERVICE CENTER ERP</h1></div>', unsafe_allow_html=True)

# --- TABS ---
tabs = st.tabs(["⚡ Bill", "📦 Stock", "🔴 Udhar", "👨‍🔧 Team", "📊 Reports", "⚙️ Profile"])

with tabs[0]: # Billing
    st.subheader("New Job Sheet")
    c1, c2 = st.columns(2)
    cust = c1.text_input("Customer Name")
    v_no = c2.text_input("Vehicle Number")
    labor = c1.number_input("Labor Charges (₹)", 0.0)
    parts_amt = c2.number_input("Parts Total (₹)", 0.0)
    pay_mode = c1.selectbox("Payment Mode", ["Cash", "UPI/Online", "Udhar"])
    paid = c2.number_input("Paid Amount", 0.0)
    work = st.text_area("Work Details")
    if st.button("💾 Save Bill"):
        udhar = (labor + parts_amt) - paid
        c.execute("INSERT INTO bills (customer, vehicle, labor_charge, parts_total, final_total, paid, udhar, payment_mode, date, work_details) VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (cust, v_no, labor, parts_amt, labor+parts_amt, paid, udhar, pay_mode, datetime.now().strftime("%Y-%m-%d"), work))
        conn.commit()
        st.success("Bill Saved!")

with tabs[1]: # Stock
    st.subheader("Inventory (MRP & Selling)")
    with st.expander("➕ Add New Part"):
        name = st.text_input("Part Name")
        mrp = st.number_input("MRP")
        sp = st.number_input("Selling Price")
        stk = st.number_input("Stock", 0)
        if st.button("Add Part"):
            c.execute("INSERT INTO inventory (name, mrp, selling_price, stock) VALUES (?,?,?,?)", (name, mrp, sp, stk))
            conn.commit()
    st.dataframe(pd.read_sql("SELECT * FROM inventory", conn), use_container_width=True)

with tabs[2]: # Udhar
    st.subheader("🔴 Udhar Khata")
    st.dataframe(pd.read_sql("SELECT customer, vehicle, udhar FROM bills WHERE udhar > 0", conn), use_container_width=True)

with tabs[3]: # Team
    st.subheader("👨‍🔧 Mechanics")
    m_name = st.text_input("Mechanic Name")
    if st.button("Add Mechanic"):
        c.execute("INSERT INTO mechanics (name) VALUES (?)", (m_name,))
        conn.commit()
    st.table(pd.read_sql("SELECT * FROM mechanics", conn))

with tabs[4]: # Reports
    st.subheader("📊 Financial Reports")
    df = pd.read_sql("SELECT labor_charge, parts_total, payment_mode, date FROM bills", conn)
    df['date'] = pd.to_datetime(df['date'])
    st.write("Monthly Turnover (Labor vs Parts)")
    st.dataframe(df.groupby(df['date'].dt.to_period('M'))[['labor_charge', 'parts_total']].sum(), use_container_width=True)

with tabs[5]: # Profile
    st.subheader("⚙️ Garage Settings")
    st.write("Garage profile settings here...")
  
