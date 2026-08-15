import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# Page Configuration
st.set_page_config(page_title="Pro Garage ERP", layout="wide", page_icon="🏎️")

# 🎨 ULTRA-MODERN 3D CSS STYLING
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1e293b, #0f172a, #020617);
        color: #f8fafc;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    
    section[data-testid="stSidebar"] { display: none; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .header-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.125);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 20px 30px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.2);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 12px 24px !important;
        box-shadow: 0 10px 20px rgba(29, 78, 216, 0.35), inset 0 2px 2px rgba(255, 255, 255, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 15px 25px rgba(29, 78, 216, 0.5), inset 0 2px 2px rgba(255, 255, 255, 0.5) !important;
    }

    .stat-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 8px 8px 16px #080d1a, -8px -8px 16px #16233e;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(15, 23, 42, 0.6);
        padding: 8px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 600;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Database Connection
conn = sqlite3.connect('garage_billing_v2.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS inventory 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, price REAL, stock INTEGER, alert_level INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS mechanics 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS garage_profile 
             (id INTEGER PRIMARY KEY DEFAULT 1, name TEXT, address TEXT, phone TEXT, tagline TEXT)''')
c.execute("INSERT OR IGNORE INTO garage_profile (id, name, address, phone, tagline) VALUES (1, 'MY GARAGE & AUTO SERVICE', 'Main Road, City', '9876543210', 'Best Service Guaranteed')")
c.execute('''CREATE TABLE IF NOT EXISTS bills 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, phone TEXT, vehicle TEXT, labor_charge REAL, 
              parts_total REAL, gst_percent REAL, final_total REAL, paid REAL, udhar REAL, date TEXT, 
              mechanic TEXT, work_details TEXT)''')
conn.commit()

c.execute("SELECT name, address, phone, tagline FROM garage_profile WHERE id = 1")
g_name, g_address, g_phone, g_tagline = c.fetchone()

# 🏎️ 3D Header Banner
st.markdown(f"""
<div class="header-card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1 style='color: #60a5fa; margin:0; font-size: 32px; font-weight:800;'>✨ {g_name}</h1>
            <p style='color: #94a3b8; margin:6px 0 0 0; font-size:14px;'>📍 {g_address} &nbsp;|&nbsp; 📞 {g_phone} &nbsp;|&nbsp; <i>{g_tagline}</i></p>
        </div>
        <div style="background: rgba(59, 130, 246, 0.15); padding: 10px 18px; border-radius: 30px; border: 1px solid rgba(59, 130, 246, 0.3);">
            <span style="color:#60a5fa; font-weight:700;">PRO ERP v3.0</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 📌 Top 3D Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⚡ Quick Billing", 
    "📦 Stock & Orders", 
    "🔴 Udhar Khata", 
    "👨‍🔧 Mechanics", 
    "📜 History", 
    "⚙️ Profile"
])

# ----------------- 1. QUICK BILLING -----------------
with tab1:
    st.subheader("📝 Create New Bill / Job Sheet")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        cust_name = st.text_input("Customer Name")
        cust_phone = st.text_input("WhatsApp Number (e.g. 919876543210)")
    with col2:
        vehicle_no = st.text_input("Vehicle Number").upper()
    with col3:
        c.execute("SELECT name FROM mechanics")
        mech_list = [m[0] for m in c.fetchall()]
        selected_mech = st.selectbox("Assigned Mechanic", mech_list if mech_list else ["Default"])

    work_desc = st.text_area("🔧 Services Performed / Work Details", placeholder="Example: Engine Oil Change, Washing, Brake Pad Replacement...")

    st.divider()
    
    c.execute("SELECT name, price, stock FROM inventory WHERE stock > 0")
    parts = c.fetchall()
    
    parts_cost = 0.0
    items = []
    if parts:
        part_dict = {p[0]: (p[1], p[2]) for p in parts}
        items = st.multiselect("📦 Select Spare Parts Used", list(part_dict.keys()))
        for item in items:
            price, _ = part_dict[item]
            parts_cost += price
    
    col_a, col_b = st.columns(2)
    with col_a:
        labor_charge = st.number_input("Labor Charges (₹)", min_value=0.0, value=0.0)
        subtotal = parts_cost + labor_charge
        gst_percent = st.selectbox("GST Rate (%)", [0, 5, 12, 18, 28])
        gst_amount = (subtotal * gst_percent) / 100
        final_total = subtotal + gst_amount
        st.markdown(f"<div class='stat-card'><h3 style='color: #4ade80; margin:0;'>Total Amount: ₹{final_total:.2f}</h3></div>", unsafe_allow_html=True)

    with col_b:
        paid = st.number_input("Paid Amount (₹)", min_value=0.0, value=final_total)
        udhar = final_total - paid
        
        st.write("")
        if st.button("💾 Save Bill & Share WhatsApp", use_container_width=True):
            if not cust_name or not vehicle_no:
                st.error("Please enter Customer Name and Vehicle Number!")
            else:
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                c.execute('''INSERT INTO bills (customer, phone, vehicle, labor_charge, parts_total, gst_percent, final_total, paid, udhar, date, mechanic, work_details) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (cust_name, cust_phone, vehicle_no, labor_charge, parts_cost, gst_percent, final_total, paid, udhar, date_str, selected_mech, work_desc))
                
                for item in items:
                    c.execute("UPDATE inventory SET stock = stock - 1 WHERE name = ?", (item,))
                conn.commit()
                
                st.success("✅ Bill Saved Successfully!")
                
                msg = (
                    f"🏎️ *{g_name}*\n"
                    f"📍 {g_address}\n"
                    f"📞 {g_phone}\n"
                    f"-----------------------------------\n"
                    f"👤 *Customer Name:* {cust_name}\n"
                    f"🚘 *Vehicle No:* {vehicle_no}\n"
                    f"📅 *Date:* {date_str}\n"
                    f"-----------------------------------\n"
                    f"🔧 *Work Details:* \n{work_desc}\n"
                    f"-----------------------------------\n"
                    f"📦 *Parts Charges:* ₹{parts_cost:.2f}\n"
                    f"👨‍🔧 *Labor Charges:* ₹{labor_charge:.2f}\n"
                    f"💰 *Total Bill:* ₹{final_total:.2f}\n"
                    f"✅ *Paid Amount:* ₹{paid:.2f}\n"
                    f"🔴 *Pending Udhar:* ₹{udhar:.2f}\n"
                    f"-----------------------------------\n"
                    f"🙏 *धन्यवाद! आप हमारे यहाँ बार-बार आएं।*"
                )
                
                # URLLIB ENCODING FIX
                encoded_msg = urllib.parse.quote(msg)
                wa_url = f"https://wa.me/{cust_phone}?text={encoded_msg}"
                st.markdown(f"[📲 **Click Here to Send Full WhatsApp Bill**]({wa_url})", unsafe_allow_html=True)

# ----------------- 2. STOCK & CUSTOM ORDERS -----------------
with tab2:
    st.subheader("📦 Inventory & Supplier Order Manager")
    
    with st.expander("➕ Add New Spare Part"):
        p_name = st.text_input("Part Name")
        p_cat = st.selectbox("Category", ["Engine Oil", "Brakes", "Tyres", "Electrical", "General Spare", "Services"])
        p_price = st.number_input("Selling Price (₹)", min_value=0.0)
        p_stock = st.number_input("Stock Quantity", min_value=0, value=10)
        p_alert = st.number_input("Low Stock Alert Level", min_value=1, value=3)
        
        if st.button("Save Part"):
            c.execute("INSERT INTO inventory (name, category, price, stock, alert_level) VALUES (?, ?, ?, ?, ?)",
                      (p_name, p_cat, p_price, p_stock, p_alert))
            conn.commit()
            st.success(f"{p_name} added to stock!")

    st.divider()
    
    st.subheader("🛍️ Create Custom Supplier Order")
    c.execute("SELECT name, stock FROM inventory")
    all_inventory = c.fetchall()
    
    if all_inventory:
        inv_dict = {item[0]: item[1] for item in all_inventory}
        selected_order_items = st.multiselect("चुने कि किन-किन आइटम्स का ऑर्डर भेजना है:", list(inv_dict.keys()))
        
        if selected_order_items:
            order_text = f"📦 *NEW STOCK REQUIREMENT ORDER*\nGarage: *{g_name}*\n-----------------------------------\n"
            
            for item in selected_order_items:
                req_qty = st.number_input(f"Quantity for '{item}' (Current Stock: {inv_dict[item]})", min_value=1, value=5, key=f"req_{item}")
                order_text += f"• {item} - Qty: {req_qty} Pcs\n"
                
            order_text += "-----------------------------------\nकृपया सामान जल्द भिजवाएं। धन्यवाद!"
            
            supplier_phone = st.text_input("Supplier WhatsApp Number (e.g. 919876543210)")
            
            if supplier_phone:
                encoded_order_msg = urllib.parse.quote(order_text)
                order_wa_url = f"https://wa.me/{supplier_phone}?text={encoded_order_msg}"
                st.markdown(f"[📲 **Share Order via WhatsApp**]({order_wa_url})", unsafe_allow_html=True)

    st.divider()
    st.subheader("📊 Current Inventory")
    df = pd.read_sql_query("SELECT id, name, category, price, stock, alert_level FROM inventory", conn)
    st.dataframe(df, use_container_width=True)

# ----------------- 3. UDHAR KHATA -----------------
with tab3:
    st.subheader("🔴 Udhar Khata")
    df_udhar = pd.read_sql_query("SELECT id, customer, phone, vehicle, final_total, paid, udhar, date FROM bills WHERE udhar > 0", conn)
    if not df_udhar.empty:
        st.metric("Total Market Udhar", f"₹{df_udhar['udhar'].sum():.2f}")
        st.dataframe(df_udhar, use_container_width=True)
    else:
        st.success("🎉 Zero Udhar!")

# ----------------- 4. MECHANICS -----------------
with tab4:
    st.subheader("👨‍🔧 Manage Mechanics")
    m_name = st.text_input("Mechanic Name")
    m_phone = st.text_input("Phone Number")
    if st.button("Add Mechanic"):
        c.execute("INSERT INTO mechanics (name, phone) VALUES (?, ?)", (m_name, m_phone))
        conn.commit()
        st.success("Mechanic Added!")
    df_m = pd.read_sql_query("SELECT * FROM mechanics", conn)
    st.table(df_m)

# ----------------- 5. HISTORY -----------------
with tab5:
    st.subheader("📜 Service History")
    search_v = st.text_input("🔍 Search Vehicle Number").upper()
    if search_v:
        df_v = pd.read_sql_query("SELECT customer, vehicle, work_details, final_total, paid, udhar, date FROM bills WHERE vehicle LIKE ?", conn, params=(f"%{search_v}%",))
        st.dataframe(df_v, use_container_width=True)
    else:
        df_all = pd.read_sql_query("SELECT id, customer, vehicle, work_details, final_total, paid, udhar, date FROM bills", conn)
        st.dataframe(df_all, use_container_width=True)

# ----------------- 6. PROFILE -----------------
with tab6:
    st.subheader("⚙️ Garage Profile Settings")
    with st.form("garage_form"):
        new_name = st.text_input("Garage Name", value=g_name)
        new_address = st.text_area("Address", value=g_address)
        new_phone = st.text_input("Phone Number", value=g_phone)
        new_tagline = st.text_input("Tagline", value=g_tagline)
        
        if st.form_submit_button("Save Details"):
            c.execute("UPDATE garage_profile SET name=?, address=?, phone=?, tagline=? WHERE id=1", 
                      (new_name, new_address, new_phone, new_tagline))
            conn.commit()
            st.success("✅ Saved!")
        
