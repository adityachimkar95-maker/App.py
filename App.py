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
c.execute("INSERT OR IGNORE INTO garage_profile (id, name, address, phone, tagline) VALUES (1, 'MY AUTO SERVICE CENTER', 'Malkapur Main Road, Chikhli', '9158551896', 'Best Service Guaranteed')")
c.execute('''CREATE TABLE IF NOT EXISTS bills (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, vehicle TEXT, labor_charge REAL, parts_total REAL, final_total REAL, paid REAL, udhar REAL, payment_mode TEXT, date TEXT, mechanic TEXT, work_details TEXT)''')
conn.commit()

c.execute("SELECT name, address, phone, tagline FROM garage_profile WHERE id = 1")
g_name, g_address, g_phone, g_tagline = c.fetchone()

# --- PREMIUM COMPACT UI ---
st.markdown("""
<style>
    .stApp { background: #0f172a; color: #f8fafc; font-family: sans-serif; }
    
    /* Compact Header Box */
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-title {
        color: #fbbf24 !important;
        margin: 0 !important;
        font-size: 15px !important;
        font-weight: 800 !important;
    }
    .header-sub {
        color: #94a3b8 !important;
        margin: 2px 0 0 0 !important;
        font-size: 10px !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: #0f172a !important;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    
    /* Tabs font size for mobile */
    .stTabs [data-baseweb="tab"] {
        font-size: 11px !important;
        font-weight: 600;
        padding: 6px 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown(f"""
<div class="header-card">
    <div>
        <h1 class="header-title">🏎️ {g_name}</h1>
        <p class="header-sub">📍 {g_address} &nbsp;|&nbsp; 📞 {g_phone}</p>
    </div>
    <div style="background: rgba(245, 158, 11, 0.15); padding: 3px 6px; border-radius: 5px;">
        <span style="color:#fbbf24; font-weight:800; font-size:9px;">PRO</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- TABS ---
tabs = st.tabs(["⚡ Bill", "📦 Stock", "🔴 Udhar", "👨‍🔧 Team", "📊 Report", "⚙️ Profile"])

with tabs[0]: # Billing
    st.subheader("📝 New Bill / Job Sheet")
    c1, c2 = st.columns(2)
    cust = c1.text_input("Customer Name")
    v_no = c2.text_input("Vehicle Number")
    labor = c1.number_input("Labor Charges (₹)", 0.0)
    parts_amt = c2.number_input("Parts Total (₹)", 0.0)
    pay_mode = c1.selectbox("Payment Mode", ["Cash", "UPI/Online", "Udhar"])
    paid = c2.number_input("Paid Amount", 0.0, value=labor+parts_amt)
    work = st.text_area("Work Details")
    
    if st.button("💾 Save Bill", use_container_width=True):
        final = labor + parts_amt
        udhar = final - paid
        c.execute("INSERT INTO bills (customer, vehicle, labor_charge, parts_total, final_total, paid, udhar, payment_mode, date, work_details) VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (cust, v_no, labor, parts_amt, final, paid, udhar, pay_mode, datetime.now().strftime("%Y-%m-%d"), work))
        conn.commit()
        st.success("✅ Bill Saved Successfully!")

with tabs[1]: # Stock
    st.subheader("📦 Inventory (MRP & Selling)")
    with st.expander("➕ Add New Spare Part"):
        name = st.text_input("Part Name")
        mrp = st.number_input("MRP (₹)", 0.0)
        sp = st.number_input("Selling Price (₹)", 0.0)
        stk = st.number_input("Stock Qty", 0)
        if st.button("Save Part"):
            c.execute("INSERT INTO inventory (name, mrp, selling_price, stock) VALUES (?,?,?,?)", (name, mrp, sp, stk))
            conn.commit()
            st.success("Part Added!")
    st.dataframe(pd.read_sql("SELECT * FROM inventory", conn), use_container_width=True)

with tabs[2]: # Udhar
    st.subheader("🔴 Market Udhar Khata")
    df_u = pd.read_sql("SELECT customer, vehicle, udhar FROM bills WHERE udhar > 0", conn)
    if not df_u.empty:
        st.metric("Total Udhar", f"₹{df_u['udhar'].sum():.2f}")
        st.dataframe(df_u, use_container_width=True)
    else:
        st.success("🎉 Zero Udhar!")

with tabs[3]: # Team
    st.subheader("👨‍🔧 Manage Mechanics")
    m_name = st.text_input("Mechanic Name")
    m_ph = st.text_input("Phone Number")
    if st.button("Add Mechanic"):
        c.execute("INSERT INTO mechanics (name, phone) VALUES (?,?)", (m_name, m_ph))
        conn.commit()
        st.success("Mechanic Added!")
    st.table(pd.read_sql("SELECT * FROM mechanics", conn))

with tabs[4]: # Reports
    st.subheader("📊 Turnover Reports")
    df = pd.read_sql("SELECT labor_charge, parts_total, payment_mode, date FROM bills", conn)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        st.write("##### Monthly Breakdown")
        st.dataframe(df.groupby(df['date'].dt.to_period('M'))[['labor_charge', 'parts_total']].sum(), use_container_width=True)
        st.write("##### Payment Mode Split")
        st.dataframe(df.groupby('payment_mode')[['labor_charge', 'parts_total']].sum(), use_container_width=True)
    else:
        st.info("No sales data available yet.")

with tabs[5]: # Profile
    st.subheader("⚙️ Garage Settings")
    with st.form("profile_form"):
        p_name = st.text_input("Service Center Name", value=g_name)
        p_addr = st.text_area("Address", value=g_address)
        p_phone = st.text_input("Phone Number", value=g_phone)
        p_tag = st.text_input("Tagline", value=g_tagline)
        
        if st.form_submit_button("Update Profile"):
            c.execute("UPDATE garage_profile SET name=?, address=?, phone=?, tagline=? WHERE id=1", (p_name, p_addr, p_phone, p_tag))
            conn.commit()
            st.success("✅ Profile Updated! Refresh page to see changes.")
        
