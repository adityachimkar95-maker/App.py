import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database Setup
conn = sqlite3.connect('garage_billing.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS inventory 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, price REAL, stock INTEGER, alert_level INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS bills 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, phone TEXT, vehicle TEXT, total REAL, paid REAL, udhar REAL, date TEXT)''')

conn.commit()

# App Interface
st.set_page_config(page_title="Automobile Garage Billing", layout="wide")
st.title("🚗 Automobile Garage Billing & Stock Manager")

menu = ["Billing System", "Stock Management", "Udhar Khata", "Sales Summary"]
choice = st.sidebar.selectbox("Navigation", menu)

# 1. Billing System
if choice == "Billing System":
    st.header("📝 Create New Bill")
    c.execute("SELECT name, price, stock FROM inventory WHERE stock > 0")
    parts = c.fetchall()
    
    col1, col2 = st.columns(2)
    with col1:
        cust_name = st.text_input("Customer Name")
        cust_phone = st.text_input("WhatsApp Number")
    with col2:
        vehicle_no = st.text_input("Vehicle Number")
        
    st.divider()
    
    if parts:
        part_dict = {p[0]: (p[1], p[2]) for p in parts}
        selected_part = st.selectbox("Select Spare Part", list(part_dict.keys()))
        price, available_stock = part_dict[selected_part]
        
        st.info(f"Price: ₹{price} | Available Stock: {available_stock}")
        qty = st.number_input("Quantity", min_value=1, max_value=available_stock, value=1)
        
        total_amount = price * qty
        discount = st.number_input("Discount (₹)", min_value=0.0, value=0.0)
        final_amount = total_amount - discount
        
        st.subheader(f"Final Amount: ₹{final_amount}")
        paid = st.number_input("Paid Amount (₹)", min_value=0.0, max_value=final_amount, value=final_amount)
        udhar = final_amount - paid
        
        if st.button("Generate Bill & Save"):
            c.execute("UPDATE inventory SET stock = stock - ? WHERE name = ?", (qty, selected_part))
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute("INSERT INTO bills (customer, phone, vehicle, total, paid, udhar, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (cust_name, cust_phone, vehicle_no, final_amount, paid, udhar, date_str))
            conn.commit()
            st.success("Bill Saved Successfully!")
            
            msg = f"Hello {cust_name}, your bill total is Rs.{final_amount}. Paid: Rs.{paid}, Pending Dues: Rs.{udhar}. Thank you!"
            wa_url = f"https://wa.me/{cust_phone}?text={msg.replace(' ', '%20')}"
            st.markdown(f"[📲 Send Bill via WhatsApp]({wa_url})", unsafe_allow_html=True)
    else:
        st.warning("No items in stock! Please add spare parts in Stock Management first.")

# 2. Stock Management
elif choice == "Stock Management":
    st.header("📦 Inventory & Stock")
    with st.expander("➕ Add New Spare Part"):
        p_name = st.text_input("Part Name")
        p_cat = st.text_input("Category (e.g. Engine, Brakes)")
        p_price = st.number_input("Unit Price (₹)", min_value=0.0)
        p_stock = st.number_input("Initial Stock Quantity", min_value=0)
        p_alert = st.number_input("Low Stock Alert Level", min_value=1, value=5)
        
        if st.button("Add Item"):
            c.execute("INSERT INTO inventory (name, category, price, stock, alert_level) VALUES (?, ?, ?, ?, ?)",
                      (p_name, p_cat, p_price, p_stock, p_alert))
            conn.commit()
            st.success(f"{p_name} added to inventory!")

    df = pd.read_sql_query("SELECT id, name, category, price, stock, alert_level FROM inventory", conn)
    st.dataframe(df, use_container_width=True)
    
    low_stock = df[df['stock'] <= df['alert_level']]
    if not low_stock.empty:
        st.error("⚠️ LOW STOCK WARNING:")
        st.table(low_stock[['name', 'stock', 'alert_level']])

# 3. Udhar Khata
elif choice == "Udhar Khata":
    st.header("🔴 Udhar Khata (Pending Payments)")
    df_udhar = pd.read_sql_query("SELECT * FROM bills WHERE udhar > 0", conn)
    if not df_udhar.empty:
        st.dataframe(df_udhar, use_container_width=True)
        st.metric("Total Outstanding Udhar", f"₹{df_udhar['udhar'].sum()}")
    else:
        st.success("Great news! No pending dues.")

# 4. Sales Summary
elif choice == "Sales Summary":
    st.header("📊 Sales Dashboard")
    df_sales = pd.read_sql_query("SELECT * FROM bills", conn)
    if not df_sales.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"₹{df_sales['total'].sum()}")
        col2.metric("Cash Collected", f"₹{df_sales['paid'].sum()}")
        col3.metric("Total Udhar", f"₹{df_sales['udhar'].sum()}")
        st.bar_chart(df_sales, x='date', y='total')
    else:
        st.info("No sales data available yet.")
      
