import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(page_title="Pro Garage ERP", layout="wide", page_icon="🏎️")

# --- DATABASE SETUP ---
conn = sqlite3.connect("garage_billing_final.db", check_same_thread=False)
c = conn.cursor()

# Tables Setup
c.execute('''CREATE TABLE IF NOT EXISTS inventory 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, mrp REAL, selling_price REAL, stock INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS bills 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, vehicle TEXT, labor_charge REAL, 
              parts_total REAL, final_total REAL, paid REAL, udhar REAL, payment_mode TEXT, date TEXT)''')
conn.commit()

# --- PREMIUM UI STYLING ---
st.markdown("""
<style>
    .stApp { background: #0f172a; color: #f8fafc; }
    .header-card { background: #1e293b; padding: 15px; border-radius: 12px; border-left: 6px solid #fbbf24; margin-bottom: 20px; }
    h1 { color: #fbbf24 !important; font-size: 24px !important; }
    .stButton>button { background: linear-gradient(135deg, #f59e0b, #d97706); color: #0f172a; font-weight: bold; width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="header-card"><h1>🏎️ AUTO SERVICE CENTER ERP</h1></div>', unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["⚡ New Billing", "📦 Inventory", "📊 Turnover Reports"])

with tab1:
    st.subheader("Add New Bill")
    c1, c2 = st.columns(2)
    cust = c1.text_input("Customer Name")
    v_no = c2.text_input("Vehicle Number")
    
    labor = c1.number_input("Labor Charges (₹)", 0.0)
    parts_amt = c2.number_input("Parts Total (₹)", 0.0)
    
    final_total = labor + parts_amt
    paid = c1.number_input("Paid Amount (₹)", min_value=0.0, value=final_total)
    pay_mode = c2.selectbox("Payment Mode", ["Cash", "UPI/Online", "Udhar"])
    udhar = final_total - paid
    
    if st.button("💾 Save Bill"):
        date_now = datetime.now().strftime("%Y-%m-%d")
        c.execute("INSERT INTO bills (customer, vehicle, labor_charge, parts_total, final_total, paid, udhar, payment_mode, date) VALUES (?,?,?,?,?,?,?,?,?)",
                  (cust, v_no, labor, parts_amt, final_total, paid, udhar, pay_mode, date_now))
        conn.commit()
        st.success(f"✅ Bill Saved! (Mode: {pay_mode})")

with tab2:
    st.subheader("Manage Inventory")
    with st.expander("➕ Add New Spare Part"):
        name = st.text_input("Part Name")
        mrp = st.number_input("MRP (₹)", 0.0)
        s_price = st.number_input("Selling Price (₹)", 0.0)
        stock = st.number_input("Current Stock", 0)
        if st.button("Add Part to Stock"):
            c.execute("INSERT INTO inventory (name, mrp, selling_price, stock) VALUES (?,?,?,?)", (name, mrp, s_price, stock))
            conn.commit()
            st.success("Item Added!")
            
    st.write("### Current Stock List")
    st.dataframe(pd.read_sql("SELECT * FROM inventory", conn), use_container_width=True)

with tab3:
    st.subheader("📊 Financial Reports")
    df = pd.read_sql("SELECT labor_charge, parts_total, payment_mode, date FROM bills", conn)
    df['date'] = pd.to_datetime(df['date'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("##### Monthly Turnover")
        st.dataframe(df.groupby(df['date'].dt.to_period('M'))[['labor_charge', 'parts_total']].sum())
    with col2:
        st.write("##### Payment Mode Split")
        st.dataframe(df.groupby('payment_mode')['parts_total'].sum())
                      
