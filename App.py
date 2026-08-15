import sqlite3
import urllib.parse
from datetime import datetime
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(page_title="Pro Garage ERP", layout="wide", page_icon="🏎️")

# 🎨 LUXURY MODERN AUTOMOTIVE DASHBOARD THEME
st.markdown(
    """
    <style>
    /* Main Background & Fonts */
    .stApp {
        background: #0f172a !important; /* Rich Dark Slate Background */
        color: #f8fafc !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    section[data-testid="stSidebar"] { display: none; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Typography Overrides */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    label {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        margin-bottom: 4px !important;
    }

    /* Ultra-Compact & Sleek Header Card */
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(245, 158, 11, 0.3); /* Gold Accent Border */
        border-radius: 10px;
        padding: 6px 12px;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-title {
        color: #fbbf24 !important; /* Warm Gold */
        margin: 0 !important;
        font-size: 14px !important;
        font-weight: 800 !important;
        letter-spacing: 0.2px;
        line-height: 1.2;
    }
    
    .header-sub {
        color: #94a3b8 !important;
        margin: 2px 0 0 0 !important;
        font-size: 10px !important;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Input Fields Styling (Sleek Dark Fields) */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, 
    .stSelectbox>div>div>div, 
    .stNumberInput>div>div>input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        padding: 8px 12px !important;
    }
    
    .stTextInput>div>div>input:focus, 
    .stTextArea>div>div>textarea:focus {
        border-color: #f59e0b !important;
        box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2) !important;
    }

    /* Tabs Styling (Pill Shaped Mobile Bar) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #1e293b;
        padding: 4px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #94a3b8 !important;
        font-weight: 600;
        padding: 6px 12px;
        font-size: 12px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #0f172a !important;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3) !important;
    }
    
    .stTabs [aria-selected="true"] span {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    /* High-Quality Action Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #0f172a !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border: none !important;
        padding: 10px 16px !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25) !important;
        transition: all 0.2s ease-in-out;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(245, 158, 11, 0.35) !important;
    }

    .stButton>button span {
        color: #0f172a !important;
    }

    /* Total & Stat Card */
    .stat-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-radius: 10px;
        padding: 12px;
        border: 1px solid rgba(245, 158, 11, 0.3);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .stat-card h3 {
        color: #10b981 !important; /* Green for total money */
        margin: 0 !important;
        font-size: 16px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Database Connection
conn = sqlite3.connect("garage_billing_v2.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS inventory 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, price REAL, stock INTEGER, alert_level INTEGER)""")
c.execute("""CREATE TABLE IF NOT EXISTS mechanics 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS garage_profile 
             (id INTEGER PRIMARY KEY DEFAULT 1, name TEXT, address TEXT, phone TEXT, tagline TEXT)""")
c.execute(
    "INSERT OR IGNORE INTO garage_profile (id, name, address, phone, tagline) VALUES (1, 'MY AUTO SERVICE CENTER', 'Malkapur Main Road, Chikhli', '9158551896', 'Best Service Guaranteed')"
)
c.execute("""CREATE TABLE IF NOT EXISTS bills 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, phone TEXT, vehicle TEXT, labor_charge REAL, 
              parts_total REAL, gst_percent REAL, final_total REAL, paid REAL, udhar REAL, date TEXT, 
              mechanic TEXT, work_details TEXT)""")
conn.commit()

c.execute("SELECT name, address, phone, tagline FROM garage_profile WHERE id = 1")
g_name, g_address, g_phone, g_tagline = c.fetchone()

# 🏎️ Extra-Compact Mobile Header Box
st.markdown(
    f"""
<div class="header-card">
    <div>
        <h1 class="header-title">🏎️ {g_name}</h1>
        <div class="header-sub">
            <span>📍 {g_address}</span>
            <span>•</span>
            <span>📞 {g_phone}</span>
        </div>
    </div>
    <div style="background: rgba(245, 158, 11, 0.15); padding: 3px 6px; border-radius: 5px; border: 1px solid rgba(245, 158, 11, 0.4);">
        <span style="color:#fbbf24; font-weight:800; font-size:9px;">PRO v3.0</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# 📌 Navigation Tabs (Compact Labels)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["⚡ Bill", "📦 Stock", "🔴 Udhar", "👨‍🔧 Team", "📜 History", "⚙️ Profile"]
)

# ----------------- 1. QUICK BILLING -----------------
with tab1:
  st.subheader("📝 New Bill / Job Sheet")

  col1, col2, col3 = st.columns(3)
  with col1:
    cust_name = st.text_input("Customer Name")
    cust_phone = st.text_input("WhatsApp Number (e.g. 919876543210)")
  with col2:
    vehicle_no = st.text_input("Vehicle Number").upper()
  with col3:
    c.execute("SELECT name FROM mechanics")
    mech_list = [m[0] for m in c.fetchall()]
    selected_mech = st.selectbox(
        "Assigned Mechanic", mech_list if mech_list else ["Default"]
    )

  work_desc = st.text_area(
      "🔧 Services Performed / Work Details",
      placeholder="Example: Engine Oil Change, Washing...",
  )

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
    st.markdown(
        f"<div class='stat-card'><h3>Total Amount: ₹{final_total:.2f}</h3></div>",
        unsafe_allow_html=True,
    )

  with col_b:
    paid = st.number_input("Paid Amount (₹)", min_value=0.0, value=final_total)
    udhar = final_total - paid

    st.write("")
    if st.button("💾 Save Bill & Share WhatsApp", use_container_width=True):
      if not cust_name or not vehicle_no:
        st.error("Please enter Customer Name and Vehicle Number!")
      else:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute(
            """INSERT INTO bills (customer, phone, vehicle, labor_charge, parts_total, gst_percent, final_total, paid, udhar, date, mechanic, work_details) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                cust_name,
                cust_phone,
                vehicle_no,
                labor_charge,
                parts_cost,
                gst_percent,
                final_total,
                paid,
                udhar,
                date_str,
                selected_mech,
                work_desc,
            ),
        )

        for item in items:
          c.execute(
              "UPDATE inventory SET stock = stock - 1 WHERE name = ?", (item,)
          )
        conn.commit()

        st.success("✅ Bill Saved Successfully!")

        msg = (
            f"🏎️ *{g_name}*\n"
            f"📍 {g_address}\n"
            f"📞 {g_phone}\n"
            "-----------------------------------\n"
            f"👤 *Customer:* {cust_name}\n"
            f"🚘 *Vehicle No:* {vehicle_no}\n"
            f"📅 *Date:* {date_str}\n"
            "-----------------------------------\n"
            f"🔧 *Work Details:* \n{work_desc}\n"
            "-----------------------------------\n"
            f"📦 *Parts Charges:* ₹{parts_cost:.2f}\n"
            f"👨‍🔧 *Labor Charges:* ₹{labor_charge:.2f}\n"
            f"💰 *Total Bill:* ₹{final_total:.2f}\n"
            f"✅ *Paid Amount:* ₹{paid:.2f}\n"
            f"🔴 *Pending Udhar:* ₹{udhar:.2f}\n"
            "-----------------------------------\n"
            "🙏 *धन्यवाद! आप हमारे यहाँ बार-बार आएं।*"
        )

        encoded_msg = urllib.parse.quote(msg)
        wa_url = f"https://wa.me/{cust_phone}?text={encoded_msg}"
        st.markdown(
            f"[📲 **Click Here to Send WhatsApp Bill**]({wa_url})",
            unsafe_allow_html=True,
        )

# ----------------- 2. STOCK & CUSTOM ORDERS -----------------
with tab2:
  st.subheader("📦 Inventory & Supplier Orders")

  with st.expander("➕ Add New Spare Part"):
    p_name = st.text_input("Part Name")
    p_cat = st.selectbox(
        "Category",
        [
            "Engine Oil",
            "Brakes",
            "Tyres",
            "Electrical",
            "General Spare",
            "Services",
        ],
    )
    p_price = st.number_input("Selling Price (₹)", min_value=0.0)
    p_stock = st.number_input("Stock Quantity", min_value=0, value=10)
    p_alert = st.number_input("Low Stock Alert Level", min_value=1, value=3)

    if st.button("Save Part"):
      c.execute(
          "INSERT INTO inventory (name, category, price, stock, alert_level)"
          " VALUES (?, ?, ?, ?, ?)",
          (p_name, p_cat, p_price, p_stock, p_alert),
      )
      conn.commit()
      st.success(f"{p_name} added to stock!")

  st.divider()

  st.subheader("🛍️ Create Supplier Order")
  c.execute("SELECT name, stock FROM inventory")
  all_inventory = c.fetchall()

  if all_inventory:
    inv_dict = {item[0]: item[1] for item in all_inventory}
    selected_order_items = st.multiselect(
        "चुने कि किन-किन आइटम्स का ऑर्डर भेजना है:", list(inv_dict.keys())
    )

    if selected_order_items:
      order_text = (
          f"📦 *NEW STOCK REQUIREMENT ORDER*\nService Center:"
          f" *{g_name}*\n-----------------------------------\n"
      )

      for item in selected_order_items:
        req_qty = st.number_input(
            f"Quantity for '{item}' (Current Stock: {inv_dict[item]})",
            min_value=1,
            value=5,
            key=f"req_{item}",
        )
        order_text += f"• {item} - Qty: {req_qty} Pcs\n"

      order_text += (
          "-----------------------------------\nकृपया सामान जल्द भिजवाएं।"
          " धन्यवाद!"
      )

      supplier_phone = st.text_input(
          "Supplier WhatsApp Number (e.g. 919876543210)"
      )

      if supplier_phone:
        encoded_order_msg = urllib.parse.quote(order_text)
        order_wa_url = (
            f"https://wa.me/{supplier_phone}?text={encoded_order_msg}"
        )
        st.markdown(
            f"[📲 **Share Order via WhatsApp**]({order_wa_url})",
            unsafe_allow_html=True,
        )

  st.divider()
  st.subheader("📊 Current Inventory")
  df = pd.read_sql_query(
      "SELECT id, name, category, price, stock, alert_level FROM inventory",
      conn,
  )
  st.dataframe(df, use_container_width=True)

# ----------------- 3. UDHAR KHATA -----------------
with tab3:
  st.subheader("🔴 Udhar Khata")
  df_udhar = pd.read_sql_query(
      "SELECT id, customer, phone, vehicle, final_total, paid, udhar, date"
      " FROM bills WHERE udhar > 0",
      conn,
  )
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
    c.execute(
        "INSERT INTO mechanics (name, phone) VALUES (?, ?)", (m_name, m_phone)
    )
    conn.commit()
    st.success("Mechanic Added!")
  df_m = pd.read_sql_query("SELECT * FROM mechanics", conn)
  st.table(df_m)

# ----------------- 5. HISTORY -----------------
with tab5:
  st.subheader("📜 Service History")
  search_v = st.text_input("🔍 Search Vehicle Number").upper()
  if search_v:
    df_v = pd.read_sql_query(
        "SELECT customer, vehicle, work_details, final_total, paid, udhar,"
        " date FROM bills WHERE vehicle LIKE ?",
        conn,
        params=(f"%{search_v}%",),
    )
    st.dataframe(df_v, use_container_width=True)
  else:
    df_all = pd.read_sql_query(
        "SELECT id, customer, vehicle, work_details, final_total, paid, udhar,"
        " date FROM bills",
        conn,
    )
    st.dataframe(df_all, use_container_width=True)

# ----------------- 6. PROFILE -----------------
with tab6:
  st.subheader("⚙️ Garage Profile Settings")
  with st.form("garage_form"):
    new_name = st.text_input("Garage/Service Center Name", value=g_name)
    new_address = st.text_area("Address", value=g_address)
    new_phone = st.text_input("Phone Number", value=g_phone)
    new_tagline = st.text_input("Tagline", value=g_tagline)

    if st.form_submit_button("Save Details"):
      c.execute(
          "UPDATE garage_profile SET name=?, address=?, phone=?, tagline=?"
          " WHERE id=1",
          (new_name, new_address, new_phone, new_tagline),
      )
      conn.commit()
      st.success("✅ Saved!")
