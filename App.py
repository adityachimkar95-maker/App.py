import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Pro Garage ERP", layout="wide", page_icon="🏎️")

# --- DATABASE SETUP ---
conn = sqlite3.connect("garage_billing_v6.db", check_same_thread=False)
c = conn.cursor()

# Tables
c.execute('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, mrp REAL, selling_price REAL, stock INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS mechanics (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS garage_profile (id INTEGER PRIMARY KEY DEFAULT 1, name TEXT, address TEXT, phone TEXT, tagline TEXT)''')
c.execute("INSERT OR IGNORE INTO garage_profile (id, name, address, phone, tagline) VALUES (1, 'MY SERVICE CENTER', 'Chikhli', '9158551896', 'Best Service')")
c.execute('''CREATE TABLE IF NOT EXISTS bills (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, vehicle TEXT, labor_charge REAL, parts_total REAL, final_total REAL, paid REAL, udhar REAL, payment_mode TEXT, date TEXT, mechanic TEXT, work_details TEXT)''')
conn.commit()

# --- CSS ---
st.markdown("""
<style>
    .stApp { background: #0f172a; color: white; }
    .header-card { background: #1e293b; padding: 10px; border-radius: 8px; border-left: 5px solid #fbbf24; margin-bottom: 15px; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div { background: #1e293b !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- TABS ---
tabs = st.tabs(["⚡ Bill", "📦 Stock", "🔴 Udhar", "👨‍🔧 Team", "📊 Report", "⚙️ Profile"])

with tabs[0]: # Billing
    st.subheader("📝 New Bill")
    c1, c2 = st.columns(2)
    cust = c1.text_input("Customer Name")
    v_no = c2.text_input("Vehicle Number")
    
    # Adding Part selection back (Fixed)
    parts_db = pd.read_sql("SELECT name, selling_price FROM inventory WHERE stock > 0", conn)
    selected_parts = st.multiselect("📦 Select Parts", parts_db['name'].tolist())
    parts_amt = parts_db[parts_db['name'].isin(selected_parts)]['selling_price'].sum()
    
    labor = st.number_input("Labor Charges (₹)", 0.0)
    final_total = parts_amt + labor
    
    col_p1, col_p2 = st.columns(2)
    pay_mode = col_p1.selectbox("Mode", ["Cash", "UPI/Online", "Udhar"])
    paid = col_p2.number_input("Paid Amount", 0.0, value=final_total)
    
    work = st.text_area("Work Details")
    
    if st.button("💾 Save Bill", use_container_width=True):
        udhar = final_total - paid
        c.execute("INSERT INTO bills (customer, vehicle, labor_charge, parts_total, final_total, paid, udhar, payment_mode, date, work_details) VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (cust, v_no, labor, parts_amt, final_total, paid, udhar, pay_mode, datetime.now().strftime("%Y-%m-%d"), work))
        conn.commit()
        st.success("✅ Bill Saved!")

with tabs[1]: # Stock
    st.subheader("📦 Inventory")
    with st.expander("➕ Add Part"):
        n = st.text_input("Part Name")
        cat = st.selectbox("Category", ["Oil", "Brake", "Tyre", "Electrical", "General"])
        mrp = st.number_input("MRP")
        sp = st.number_input("Selling Price")
        stk = st.number_input("Stock", 0)
        if st.button("Save"):
            c.execute("INSERT INTO inventory (name, category, mrp, selling_price, stock) VALUES (?,?,?,?,?)", (n, cat, mrp, sp, stk))
            conn.commit()
            st.rerun()
    st.dataframe(pd.read_sql("SELECT * FROM inventory", conn), use_container_width=True)
