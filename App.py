import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# Page Configuration
st.set_page_config(page_title="Pro Garage ERP", layout="wide", page_icon="🏎️")

# 🎨 MOBILE-OPTIMIZED CLEAN AUTOMOTIVE THEME
st.markdown("""
    <style>
    .stApp {
        background: #0f172a !important;
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif;
    }
    
    section[data-testid="stSidebar"] { display: none; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Ultra-Compact Header */
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 12px;
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

    /* Input & Fields Styling */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, 
    .stSelectbox>div>div>div, 
    .stNumberInput>div>div>input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        padding: 6px 10px !important;
    }

    /* Mobile Friendly Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #1e293b;
        padding: 4px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #94a3b8 !important;
        font-weight: 600;
        padding: 6px 10px;
        font-size: 11px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    /* Action Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #0f172a !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        border: none !important;
        padding: 8px 14px !important;
        width: 100%;
    }
    
    .stat-card {
        background: #1e293b;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Database Connection
conn = sqlite3.connect('garage_billing_v7.db', check_same_thread=False)
c = conn.cursor()

# Tables Setup with MRP, Selling Price, and Payment Mode
c.execute('''CREATE TABLE IF NOT EXISTS inventory 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, mrp REAL, selling_price REAL, stock INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS mechanics 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS garage_profile 
             (id INTEGER PRIMARY KEY DEFAULT 1, name TEXT, address TEXT, phone TEXT, tagline TEXT)''')
c.execute("INSERT OR IGNORE INTO garage_profile (id, name, address, phone, tagline) VALUES (1, 'MY AUTO SERVICE CENTER', 'Main Road, City', '9158551896', 'Best Service Guaranteed')")
c.execute('''CREATE TABLE IF NOT EXISTS bills 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, phone TEXT, vehicle TEXT, labor_charge REAL, 
              parts_total REAL, final_total REAL, paid REAL, udhar REAL, payment_mode TEXT, date TEXT, 
              mechanic TEXT, work_details TEXT)''')
conn.commit()

c.execute("SELECT name, address, phone, tagline FROM garage_profile WHERE id = 1")
g_name, g_address, g_phone, g_tagline = c.fetchone()

# Header Banner
st.markdown(f"""
<div class="header-card">
    <div>
        <h1 class="header-title">🏎️ {g_name}</h1>
        <p class="header-sub">📍 {g_address} &nbsp;|&nbsp; 📞 {g_phone}</p>
    </div>
    <div style="background: rgba(245, 158, 11, 0.15); padding: 3px 6px; border-radius: 5px; border: 1px solid rgba(245, 158, 11, 0.4);">
        <span style="color:#fbbf24; font-weight:800; font-size:9px;">PRO v4.0</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⚡ Bill", 
    "📦 Stock", 
    "🔴 Udhar", 
    "👨‍🔧 Team", 
    "📊 Reports", 
    "⚙️ Profile"
])

# ----------------- 1. QUICK BILLING -----------------
with tab1:
    st.subheader("📝 New Bill / Job Sheet")
    
    cust_name = st.text_input("Customer Name")
    cust_phone = st.text_input("WhatsApp Number (e.g. 919876543210)")
    vehicle_no = st.text_input("Vehicle Number").upper()
    
    c.execute("SELECT name FROM mechanics")
    mech_list = [m[0] for m in c.fetchall()]
    selected_mech = st.selectbox("Assigned Mechanic", mech_list if mech_list else ["Default"])

    work_desc = st.text_area("🔧 Work Details", placeholder="Engine Oil Change, Washing...")

    st.divider()
    
    # Inventory parts selection using Selling Price
    parts_db = pd.read_sql("SELECT name, selling_price FROM inventory WHERE stock > 0", conn)
    parts_cost = 0.0
    items = []
    
    if not parts_db.empty:
        part_dict = dict(zip(parts_db['name'], parts_db['selling_price']))
        items = st.multiselect("📦 Select Spare Parts Used", list(part_dict.keys()))
        for item in items:
            parts_cost += part_dict[item]
    
    labor_charge = st.number_input("Labor Charges (₹)", min_value=0.0, value=0.0)
    final_total = parts_cost + labor_charge
    
    col_p1, col_p2 = st.columns(2)
    pay_mode = col_p1.selectbox("Payment Mode", ["Cash", "UPI/Online", "Udhar"])
    paid = col_p2.number_input("Paid Amount (₹)", min_value=0.0, value=final_total)
    udhar = final_total - paid
    
    st.markdown(f"<div class='stat-card'><h4 style='color: #4ade80; margin:0;'>Total: ₹{final_total:.2f} | Udhar: ₹{udhar:.2f}</h4></div>", unsafe_allow_html=True)
    st.write("")

    if st.button("💾 Save Bill & Share WhatsApp"):
        if not cust_name or not vehicle_no:
            st.error("Please enter Customer Name and Vehicle Number!")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute('''INSERT INTO bills (customer, phone, vehicle, labor_charge, parts_total, final_total, paid, udhar, payment_mode, date, mechanic, work_details) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (cust_name, cust_phone, vehicle_no, labor_charge, parts_cost, final_total, paid, udhar, pay_mode, date_str, selected_mech, work_desc))
            
            for item in items:
                c.execute("UPDATE inventory SET stock = stock - 1 WHERE name = ?", (item,))
            conn.commit()
            
            st.success("✅ Bill Saved Successfully!")
            
            msg = (
                f"🏎️ *{g_name}*\n"
                f"📍 {g_address}\n📞 {g_phone}\n"
                f"-----------------------------------\n"
                f"👤 *Customer:* {cust_name}\n🚘 *Vehicle:* {vehicle_no}\n"
                f"📅 *Date:* {date_str}\n"
                f"-----------------------------------\n"
                f"🔧 *Work:* \n{work_desc}\n"
                f"-----------------------------------\n"
                f"📦 *Parts:* ₹{parts_cost:.2f}\n"
                f"👨‍🔧 *Labor:* ₹{labor_charge:.2f}\n"
                f"💰 *Total:* ₹{final_total:.2f}\n"
                f"💳 *Mode:* {pay_mode}\n"
                f"✅ *Paid:* ₹{paid:.2f} | 🔴 *Udhar:* ₹{udhar:.2f}\n"
                f"-----------------------------------\n"
                f"🙏 *धन्यवाद! फिर आएं।*"
            )
            
            encoded_msg = urllib.parse.quote(msg)
            wa_url = f"https://wa.me/{cust_phone}?text={encoded_msg}"
            st.markdown(f"[📲 **Send WhatsApp Bill**]({wa_url})", unsafe_allow_html=True)

# ----------------- 2. STOCK & INVENTORY -----------------
with tab2:
    st.subheader("📦 Inventory Manager")
    
    with st.expander("➕ Add New Spare Part"):
        p_name = st.text_input("Part Name")
        p_cat = st.selectbox("Category", ["Engine Oil", "Brakes", "Tyres", "Electrical", "General", "Services"])
        p_mrp = st.number_input("MRP (₹)", min_value=0.0)
        p_price = st.number_input("Selling Price (₹)", min_value=0.0)
        p_stock = st.number_input("Stock Quantity", min_value=0, value=10)
        
        if st.button("Save Part to Stock"):
            c.execute("INSERT INTO inventory (name, category, mrp, selling_price, stock) VALUES (?, ?, ?, ?, ?)",
                      (p_name, p_cat, p_mrp, p_price, p_stock))
            conn.commit()
            st.success(f"{p_name} added!")

    st.divider()
    st.subheader("📊 Current Stock")
    df = pd.read_sql_query("SELECT id, name, category, mrp, selling_price, stock FROM inventory", conn)
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

# ----------------- 5. REPORTS -----------------
with tab5:
    st.subheader("📊 Financial Reports")
    df_bills = pd.read_sql("SELECT labor_charge, parts_total, final_total, payment_mode, date FROM bills", conn)
    if not df_bills.empty:
        df_bills['date'] = pd.to_datetime(df_bills['date'])
        st.write("##### Monthly Turnover")
        st.dataframe(df_bills.groupby(df_bills['date'].dt.to_period('M'))[['labor_charge', 'parts_total', 'final_total']].sum(), use_container_width=True)
        st.write("##### Payment Mode Breakdown")
        st.dataframe(df_bills.groupby('payment_mode')['final_total'].sum(), use_container_width=True)
    else:
        st.info("No data found.")

# ----------------- 6. PROFILE -----------------
with tab6:
    st.subheader("⚙️ Garage Profile")
    with st.form("garage_form"):
        new_name = st.text_input("Service Center Name", value=g_name)
        new_address = st.text_area("Address", value=g_address)
        new_phone = st.text_input("Phone Number", value=g_phone)
        new_tagline = st.text_input("Tagline", value=g_tagline)
        
        if st.form_submit_button("Save Details"):
            c.execute("UPDATE garage_profile SET name=?, address=?, phone=?, tagline=? WHERE id=1", 
                      (new_name, new_address, new_phone, new_tagline))
            conn.commit()
            st.success("✅ Profile Updated!")
