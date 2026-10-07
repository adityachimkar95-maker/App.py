import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from supabase import create_client

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="My Shivshakti Auto Parts & Service",
    layout="wide",
    page_icon="🔧"
)

# ---------------------------------------------------------
# Supabase & SQLite Database Setup
# ---------------------------------------------------------
# Streamlit Secrets se Supabase details connect karein
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://vgpkmkeyezirxshkfudv.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def init_supabase():
    if not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase = init_supabase()

# Local SQLite Database Connection (Backup & App State)
conn = sqlite3.connect("garage_billing.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS inventory
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, price REAL, stock INTEGER, alert_level INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS bills
             (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, phone TEXT, vehicle TEXT, total REAL, paid REAL, udhar REAL, date TEXT)''')

conn.commit()

# ---------------------------------------------------------
# App Interface & Navigation
# ---------------------------------------------------------
st.title("🔧 Automobile Garage Billing & Stock Manager")

menu = ["Billing System", "Stock Management", "Udhar Khata", "Sales Summary", "Supabase Sync"]
choice = st.sidebar.selectbox("Navigation", menu)

# ---------------------------------------------------------
# 1. Billing System
# ---------------------------------------------------------
if choice == "Billing System":
    st.header("📋 Create New Bill")
    
    c.execute("SELECT name, price, stock FROM inventory WHERE stock > 0")
    parts = c.fetchall()
    
    col1, col2 = st.columns(2)
    with col1:
        cust_name = st.text_input("Customer Name")
        cust_phone = st.text_input("WhatsApp / Phone Number")
    with col2:
        vehicle_no = st.text_input("Vehicle Number")
        
    st.divider()
    
    if parts:
        part_dict = {p[0]: (p[1], p[2]) for p in parts}
        selected_part = st.selectbox("Select Spare Part", list(part_dict.keys()))
        price, available_stock = part_dict[selected_part]
        
        st.info(f"Price: ₹{price} | Available Stock: {available_stock}")
        qty = st.number_input("Quantity", min_value=1, max_value=available_stock, value=1)
        
        total_price = price * qty
        st.write(f"### Item Total: ₹{total_price}")
        
        paid_amount = st.number_input("Amount Paid", min_value=0.0, value=float(total_price))
        udhar_amount = total_price - paid_amount
        
        if udhar_amount > 0:
            st.warning(f"Udhar Amount: ₹{udhar_amount}")
            
        if st.button("Generate Bill & Update Stock"):
            # Local SQLite Update
            new_stock = available_stock - qty
            c.execute("UPDATE inventory SET stock = ? WHERE name = ?", (new_stock, selected_part))
            c.execute("INSERT INTO bills (customer, phone, vehicle, total, paid, udhar, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (cust_name, cust_phone, vehicle_no, total_price, paid_amount, udhar_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            
            # Syncing with Supabase (if connected)
            if supabase:
                try:
                    supabase.table("adityachimkar95-maker's Org").upsert({
                        "title": f"Bill: {cust_name} ({selected_part})",
                        "original_url": f"Vehicle: {vehicle_no} | Qty: {qty} | Total: ₹{total_price} | Paid: ₹{paid_amount}"
                    }).execute()
                except Exception as e:
                    st.error(f"Supabase Sync Error: {e}")

            st.success("Bill Generated and Stock Updated Successfully!")
    else:
        st.error("No spare parts available in stock. Please add stock first.")

# ---------------------------------------------------------
# 2. Stock Management
# ---------------------------------------------------------
elif choice == "Stock Management":
    st.header("📦 Inventory & Stock Management")
    
    tab1, tab2 = st.tabs(["Add New Item", "Current Inventory List"])
    
    with tab1:
        st.subheader("Add Part / Item")
        p_name = st.text_input("Part Name")
        p_cat = st.selectbox("Category", ["Engine Parts", "Brakes", "Oils & Lubricants", "Tyres", "Electricals", "General Service"])
        p_price = st.number_input("Selling Price (₹)", min_value=0.0, value=100.0)
        p_stock = st.number_input("Initial Stock Quantity", min_value=1, value=10)
        p_alert = st.number_input("Low Stock Alert Limit", min_value=1, value=2)
        
        if st.button("Add Item to Inventory"):
            if p_name:
                c.execute("INSERT INTO inventory (name, category, price, stock, alert_level) VALUES (?, ?, ?, ?, ?)",
                          (p_name, p_cat, p_price, p_stock, p_alert))
                conn.commit()
                
                # Syncing with Supabase
                if supabase:
                    try:
                        supabase.table("adityachimkar95-maker's Org").upsert({
                            "title": p_name,
                            "original_url": f"Category: {p_cat} | Price: ₹{p_price} | Initial Stock: {p_stock}"
                        }).execute()
                    except Exception as e:
                        st.error(f"Supabase Sync Error: {e}")

                st.success(f"Added {p_name} to Inventory!")
            else:
                st.warning("Please enter item name.")
                
    with tab2:
        df_stock = pd.read_sql_query("SELECT name AS 'Part Name', category AS 'Category', price AS 'Price (₹)', stock AS 'Stock Left', alert_level AS 'Alert Limit' FROM inventory", conn)
        st.dataframe(df_stock, use_container_width=True)

# ---------------------------------------------------------
# 3. Udhar Khata
# ---------------------------------------------------------
elif choice == "Udhar Khata":
    st.header("💳 Udhar Khata (Pending Customer Payments)")
    df_udhar = pd.read_sql_query("SELECT customer AS 'Customer', phone AS 'Phone', vehicle AS 'Vehicle', total AS 'Total Bill', paid AS 'Paid', udhar AS 'Pending Udhar', date AS 'Date' FROM bills WHERE udhar > 0", conn)
    
    if not df_udhar.empty:
        st.dataframe(df_udhar, use_container_width=True)
    else:
        st.success("No pending udhar records found!")

# ---------------------------------------------------------
# 4. Sales Summary
# ---------------------------------------------------------
elif choice == "Sales Summary":
    st.header("📈 Sales Report & Analytics")
    df_bills = pd.read_sql_query("SELECT * FROM bills", conn)
    
    if not df_bills.empty:
        total_sales = df_bills['total'].sum()
        total_collected = df_bills['paid'].sum()
        total_pending = df_bills['udhar'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Business", f"₹{total_sales}")
        m2.metric("Total Collected", f"₹{total_collected}")
        m3.metric("Total Udhar Pending", f"₹{total_pending}")
        
        st.divider()
        st.subheader("All Billing History")
        st.dataframe(df_bills, use_container_width=True)
    else:
        st.info("No bills generated yet.")

# ---------------------------------------------------------
# 5. Supabase Live View & Sync
# ---------------------------------------------------------
elif choice == "Supabase Sync":
    st.header("☁️ Supabase Cloud Database Status")
    
    if supabase:
        st.success("✅ Connected to Supabase Cloud Database!")
        if st.button("Refresh Cloud Data"):
            st.rerun()
        try:
            res = supabase.table("adityachimkar95-maker's Org").select("*").execute()
            if res.data:
                st.dataframe(pd.DataFrame(res.data), use_container_width=True)
            else:
                st.info("Supabase table is currently empty.")
        except Exception as e:
            st.error(f"Error fetching data from Supabase: {e}")
    else:
        st.warning("⚠️ Supabase API Key set nahi hai. Streamlit Settings > Secrets me Key daalein.")
    
