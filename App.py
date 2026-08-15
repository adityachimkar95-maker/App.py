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
             (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, phone TEXT, vehicle TEXT, labor_charge REAL, parts_total REAL, gst_percent REAL, final_total REAL, paid REAL, udhar REAL, date TEXT, mechanic TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS mechanics 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT)''')

conn.commit()

st.set_page_config(page_title="Pro Garage Billing & ERP", layout="wide")
st.title("🛠️ Pro Garage Billing & Management System")

menu = ["⚡ Quick Billing", "📦 Stock Management", "🔴 Udhar Khata", "👨‍🔧 Mechanics", "📜 History & Reports"]
choice = st.sidebar.selectbox("Navigation", menu)

# 1. Quick Billing
if choice == "⚡ Quick Billing":
    st.header("📝 Create New Job Sheet / Bill")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        cust_name = st.text_input("Customer Name")
        cust_phone = st.text_input("WhatsApp Number (10 digits)")
    with col2:
        vehicle_no = st.text_input("Vehicle Number (e.g. MH04AB1234)").upper()
        km_reading = st.number_input("Odometer (KM)", min_value=0, value=0)
    with col3:
        c.execute("SELECT name FROM mechanics")
        mech_list = [m[0] for m in c.fetchall()]
        selected_mech = st.selectbox("Assigned Mechanic", mech_list if mech_list else ["Default"])

    st.divider()
    
    # Items selection
    c.execute("SELECT name, price, stock FROM inventory WHERE stock > 0")
    parts = c.fetchall()
    
    parts_cost = 0.0
    selected_items = []
    
    st.subheader("🛠️ Spare Parts & Items")
    if parts:
        part_dict = {p[0]: (p[1], p[2]) for p in parts}
        items = st.multiselect("Select Spare Parts", list(part_dict.keys()))
        
        for item in items:
            price, max_stk = part_dict[item]
            qty = st.number_input(f"Quantity for {item} (Max: {max_stk})", min_value=1, max_value=max_stk, value=1, key=item)
            parts_cost += price * qty
            selected_items.append(f"{item} x{qty} (₹{price*qty})")
    else:
        st.info("No items in inventory yet. You can still add Labor charges below.")
        
    st.divider()
    
    # Financial Calculation
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("💰 Charges Breakdown")
        st.write(f"**Parts Cost:** ₹{parts_cost}")
        labor_charge = st.number_input("Labor / Service Charges (₹)", min_value=0.0, value=0.0)
        subtotal = parts_cost + labor_charge
        
        gst_opt = st.checkbox("Apply GST?")
        gst_percent = 0.0
        if gst_opt:
            gst_percent = st.selectbox("GST Rate (%)", [5, 12, 18, 28], index=2)
            
        gst_amount = (subtotal * gst_percent) / 100
        discount = st.number_input("Discount (₹)", min_value=0.0, value=0.0)
        final_total = subtotal + gst_amount - discount
        
        st.markdown(f"### **Final Total Amount: ₹{final_total:.2f}**")
        
    with col_b:
        st.subheader("💳 Payment Details")
        paid = st.number_input("Paid Amount (₹)", min_value=0.0, max_value=final_total, value=final_total)
        udhar = final_total - paid
        st.write(f"**Pending Udhar:** ₹{udhar:.2f}")
        
        if st.button("💾 Generate & Save Bill", type="primary", use_container_width=True):
            if not cust_name or not vehicle_no:
                st.error("Please enter Customer Name and Vehicle Number!")
            else:
                # Save to database
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                c.execute('''INSERT INTO bills (customer, phone, vehicle, labor_charge, parts_total, gst_percent, final_total, paid, udhar, date, mechanic) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (cust_name, cust_phone, vehicle_no, labor_charge, parts_cost, gst_percent, final_total, paid, udhar, date_str, selected_mech))
                
                # Deduct stock
                for item in items:
                    c.execute("UPDATE inventory SET stock = stock - 1 WHERE name = ?", (item,))
                conn.commit()
                
                st.success("✅ Bill Saved Successfully!")
                
                # WhatsApp Link
                msg = f"Hello {cust_name}, your bill for Vehicle {vehicle_no} is Total: Rs.{final_total:.2f}. Paid: Rs.{paid:.2f}, Due: Rs.{udhar:.2f}. Thank you for visiting!"
                wa_url = f"https://wa.me/{cust_phone}?text={msg.replace(' ', '%20')}"
                st.markdown(f"[📲 **Click Here to Send WhatsApp Invoice**]({wa_url})", unsafe_allow_html=True)

# 2. Stock Management
elif choice == "📦 Stock Management":
    st.header("📦 Inventory & Spare Parts Manager")
    with st.expander("➕ Add New Spare Part / Oil"):
        p_name = st.text_input("Part Name")
        p_cat = st.selectbox("Category", ["Engine Oil", "Brakes", "Tyres", "Electrical", "General Spare", "Accessories"])
        p_price = st.number_input("Selling Price (₹)", min_value=0.0)
        p_stock = st.number_input("Stock Quantity", min_value=0, value=10)
        p_alert = st.number_input("Low Stock Alert Level", min_value=1, value=3)
        
        if st.button("Save Part"):
            c.execute("INSERT INTO inventory (name, category, price, stock, alert_level) VALUES (?, ?, ?, ?, ?)",
                      (p_name, p_cat, p_price, p_stock, p_alert))
            conn.commit()
            st.success(f"{p_name} added to stock!")

    df = pd.read_sql_query("SELECT id, name, category, price, stock, alert_level FROM inventory", conn)
    st.dataframe(df, use_container_width=True)

# 3. Udhar Khata
elif choice == "🔴 Udhar Khata":
    st.header("🔴 Udhar Khata (Customer Dues)")
    df_udhar = pd.read_sql_query("SELECT id, customer, phone, vehicle, final_total, paid, udhar, date FROM bills WHERE udhar > 0", conn)
    if not df_udhar.empty:
        st.metric("Total Outstanding Market Udhar", f"₹{df_udhar['udhar'].sum():.2f}")
        st.dataframe(df_udhar, use_container_width=True)
    else:
        st.success("🎉 All dues cleared! Zero Udhar.")

# 4. Mechanics
elif choice == "👨‍🔧 Mechanics":
    st.header("👨‍🔧 Manage Mechanics & Staff")
    m_name = st.text_input("Mechanic Name")
    m_phone = st.text_input("Phone Number")
    if st.button("Add Mechanic"):
        c.execute("INSERT INTO mechanics (name, phone) VALUES (?, ?)", (m_name, m_phone))
        conn.commit()
        st.success("Mechanic Added!")
        
    df_m = pd.read_sql_query("SELECT * FROM mechanics", conn)
    st.table(df_m)

# 5. History & Reports
elif choice == "📜 History & Reports":
    st.header("📜 Vehicle Service History & Analytics")
    search_v = st.text_input("🔍 Search by Vehicle Number").upper()
    
    if search_v:
        df_v = pd.read_sql_query("SELECT * FROM bills WHERE vehicle LIKE ?", conn, params=(f"%{search_v}%",))
        st.subheader(f"History for {search_v}")
        st.dataframe(df_v, use_container_width=True)
    else:
        df_all = pd.read_sql_query("SELECT * FROM bills", conn)
        st.dataframe(df_all, use_container_width=True)
