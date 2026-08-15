import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# Page Configuration
st.set_page_config(page_title="Pro Garage ERP", layout="wide", page_icon="🏎️")

# Database Setup
conn = sqlite3.connect('garage_erp.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, mrp REAL, selling_price REAL, stock INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS bills (
    bill_id TEXT, customer_name TEXT, phone TEXT, vehicle TEXT, mechanic_name TEXT, 
    payment_mode TEXT, total REAL, paid_amount REAL, balance_due REAL, date TEXT, items TEXT)''')
conn.commit()

# --- App UI ---
st.title("🏎️ Pro Garage ERP")
tab1, tab2, tab3 = st.tabs(["📝 Billing", "📦 Inventory", "📊 Records"])

with tab1:
    st.subheader("New Service Bill")
    col1, col2 = st.columns(2)
    with col1:
        cust_name = st.text_input("Customer Name")
        phone = st.text_input("Phone Number", "91")
        mechanic = st.text_input("Mechanic Name")
    with col2:
        vehicle = st.text_input("Vehicle Number")
        pay_mode = st.selectbox("Payment Mode", ["Cash", "Online/UPI", "Udhar (Credit)"])

    if "cart" not in st.session_state: st.session_state.cart = []
    
    # Item Addition
    with st.expander("➕ Add Items/Service"):
        inv = pd.read_sql("SELECT * FROM inventory", conn)
        selected_item = st.selectbox("Select Item", ["-- Custom --"] + inv['item_name'].tolist())
        qty = st.number_input("Qty", 1, 100)
        
        if selected_item == "-- Custom --":
            custom_price = st.number_input("Selling Price (₹)", 0.0)
            if st.button("Add Custom"):
                st.session_state.cart.append({"name": "Service/Part", "price": custom_price, "qty": qty})
        else:
            row = inv[inv['item_name'] == selected_item].iloc[0]
            if st.button("Add Item"):
                st.session_state.cart.append({"name": selected_item, "price": row['selling_price'], "qty": qty})

    if st.session_state.cart:
        df_cart = pd.DataFrame(st.session_state.cart)
        df_cart['total'] = df_cart['price'] * df_cart['qty']
        st.table(df_cart)
        
        total = df_cart['total'].sum()
        paid = st.number_input("Paid Amount (₹)", 0.0, float(total), float(total))
        balance = total - paid
        
        if st.button("💾 Save & Share Bill"):
            bill_id = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            items_str = ", ".join(df_cart['name'].tolist())
            c.execute("INSERT INTO bills VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                      (bill_id, cust_name, phone, vehicle, mechanic, pay_mode, total, paid, balance, datetime.now().strftime('%Y-%m-%d'), items_str))
            conn.commit()
            
            # WhatsApp Message
            wa_msg = f"🛠️ *Bill: {bill_id}*\nCustomer: {cust_name}\nMechanic: {mechanic}\nTotal: ₹{total}\nPaid: ₹{paid}\nBalance: ₹{balance}"
            st.link_button("📲 Send via WhatsApp", f"https://wa.me/{phone}?text={urllib.parse.quote(wa_msg)}")
            st.session_state.cart = []

with tab2:
    st.subheader("Manage Inventory")
    with st.form("inv_form"):
        i_name = st.text_input("Item Name")
        i_mrp = st.number_input("MRP (₹)")
        i_price = st.number_input("Selling Price (₹)")
        i_stock = st.number_input("Stock", 0)
        if st.form_submit_button("Save Item"):
            c.execute("INSERT INTO inventory (item_name, mrp, selling_price, stock) VALUES (?,?,?,?)", (i_name, i_mrp, i_price, i_stock))
            conn.commit()
            st.rerun()
    st.dataframe(pd.read_sql("SELECT * FROM inventory", conn))

with tab3:
    st.subheader("Records")
    st.dataframe(pd.read_sql("SELECT * FROM bills", conn))
            
