import sqlite3
import urllib.parse
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Pro Garage ERP", layout="wide", page_icon="🏎️")

# --- DATABASE SETUP ---
conn = sqlite3.connect("garage_billing_v4.db", check_same_thread=False)
c = conn.cursor()

# Updated Inventory table with MRP and Selling Price
c.execute("""CREATE TABLE IF NOT EXISTS inventory 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, mrp REAL, selling_price REAL, stock INTEGER)""")
c.execute("""CREATE TABLE IF NOT EXISTS bills 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, vehicle TEXT, labor_charge REAL, 
              parts_total REAL, final_total REAL, date TEXT)""")
conn.commit()

# --- THEME STYLING ---
st.markdown("""
<style>
    .header-card { background: #1e293b; padding: 15px; border-radius: 10px; border-left: 5px solid #fbbf24; margin-bottom: 20px; }
    .stat-box { background: #0f172a; padding: 15px; border-radius: 10px; border: 1px solid #334155; text-align: center; }
    .metric-val { font-size: 20px; font-weight: bold; color: #fbbf24; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-card"><h1>🏎️ SERVICE CENTER ERP</h1></div>', unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["⚡ Billing", "📦 Inventory", "📊 Reports"])

with tab1:
    st.subheader("New Job Sheet")
    c1, c2 = st.columns(2)
    with c1:
        c_name = st.text_input("Customer Name")
        v_no = st.text_input("Vehicle Number")
    with c2:
        labor = st.number_input("Labor Charges (₹)", 0.0)
        parts_cost = st.number_input("Parts Total (₹)", 0.0)
    
    if st.button("Save Bill"):
        date_now = datetime.now().strftime("%Y-%m-%d")
        c.execute("INSERT INTO bills (customer, vehicle, labor_charge, parts_total, final_total, date) VALUES (?,?,?,?,?,?)",
                  (c_name, v_no, labor, parts_cost, labor+parts_cost, date_now))
        conn.commit()
        st.success("Bill Saved!")

with tab2:
    st.subheader("Manage Inventory")
    with st.expander("Add New Part"):
        name = st.text_input("Part Name")
        mrp = st.number_input("MRP (₹)")
        s_price = st.number_input("Selling Price (₹)")
        stock = st.number_input("Stock", 0)
        if st.button("Add Part"):
            c.execute("INSERT INTO inventory (name, mrp, selling_price, stock) VALUES (?,?,?,?)", (name, mrp, s_price, stock))
            conn.commit()
    
    df_stock = pd.read_sql("SELECT * FROM inventory", conn)
    st.dataframe(df_stock, use_container_width=True)

with tab3:
    st.subheader("Financial Turnover Report")
    df_bills = pd.read_sql("SELECT labor_charge, parts_total, date FROM bills", conn)
    df_bills['date'] = pd.to_datetime(df_bills['date'])
    
    # Monthly Aggregation
    df_bills['Month'] = df_bills['date'].dt.to_period('M')
    monthly = df_bills.groupby('Month')[['labor_charge', 'parts_total']].sum()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### Monthly Breakdown")
        st.dataframe(monthly, use_container_width=True)
    with col_b:
        st.write("### Yearly Summary")
        yearly = df_bills.groupby(df_bills['date'].dt.year)[['labor_charge', 'parts_total']].sum()
        st.dataframe(yearly, use_container_width=True)
        
