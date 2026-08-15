import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse
import json

# 🎨 Page Configuration (Mobile & Desktop Optimized)
st.set_page_config(
    page_title="My Shivshakti Auto Parts & Service",
    layout="wide",
    page_icon="🏎️"
)

# 🌟 3D & Modern Glassmorphism Styling (CSS)
st.markdown("""
    <style>
    /* Global App Theme */
    .stApp {
        background: radial-gradient(circle at top left, #1e293b, #0f172a, #020617);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Header & Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 3D Glassmorphism Header Card */
    .hero-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(245, 158, 11, 0.4);
        box-shadow: 0 10px 30px -10px rgba(245, 158, 11, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    .hero-title {
        color: #fbbf24;
        font-size: 24px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 13px;
        margin-top: 5px;
    }

    /* 3D Floating Action Cards */
    .st-emotion-cache-1r6slb0, .stat-card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    }

    /* 3D Inputs & Fields Styling */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>div, 
    .stNumberInput>div>div>input {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.6);
        padding: 10px !important;
    }

    /* 3D Glowing Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #0f172a !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
        transition: all 0.3s ease;
        width: 100%;
        padding: 10px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.6);
    }

    /* Tabs 3D Look */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.8);
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8 !important;
        font-weight: 600;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706) !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------------
conn = sqlite3.connect("autoparts_shop_final.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS parts (
        id TEXT PRIMARY KEY,
        name TEXT,
        price REAL,
        stock INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        customer_mobile TEXT,
        vehicle_number TEXT,
        vehicle_model TEXT,
        items_summary TEXT,
        parts_total REAL,
        labour_desc TEXT,
        labour_cost REAL,
        total_bill REAL,
        amount_paid REAL,
        balance_due REAL,
        payment_mode TEXT,
        date TEXT
    )
''')

# Insert Demo Parts if empty
cursor.execute("SELECT COUNT(*) FROM parts")
if cursor.fetchone()[0] == 0:
    demo_parts = [
        ("101", "Brake Pad Front", 1200.0, 15),
        ("102", "Engine Oil Filter", 350.0, 10),   
        ("103", "Clutch Plate Assembly", 4500.0, 5), 
        ("104", "Wiper Blade Set", 250.0, 50),
        ("105", "Air Filter", 450.0, 8),
        ("106", "Brake Shoe Rear", 850.0, 12)
    ]
    cursor.executemany("INSERT INTO parts VALUES (?, ?, ?, ?)", demo_parts)
    conn.commit()

# --------------------------------------------------------
# UI HEADER
# --------------------------------------------------------
st.markdown("""
    <div class="hero-card">
        <p class="hero-title">🏎️ MY SHIVSHAKTI AUTO PARTS & SERVICE</p>
        <p class="hero-sub">📍 Main Road, Rantham, Chikhli, Malkapur (MH) | 📞 9158551896</p>
    </div>
""", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🛒 Estimate & Billing", "📦 Inventory Stock", "📖 Udhar Khata", "📊 Records"])

# --------------------------------------------------------
# TAB 1: ESTIMATE & BILLING (SEARCH & LIVE PREVIEW)
# --------------------------------------------------------
with tab1:
    st.subheader("📝 New Customer Estimate Panel")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        c_name = st.text_input("Customer Name", placeholder="e.g. Aditya Chimkar")
        c_mobile = st.text_input("Customer Mobile Number", placeholder="9158551896")
    with col_c2:
        v_number = st.text_input("Vehicle Number", placeholder="MH19CH9695").upper()
        v_model = st.text_input("Vehicle Model", placeholder="Swift / Splendor")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    st.markdown("---")
    st.markdown("### 🔎 Search & Add Spare Parts")
    
    search_query = st.text_input("Search Part by Name or ID", placeholder="Type brake, oil, filter...")
    
    if search_query:
        cursor.execute("SELECT * FROM parts WHERE name LIKE ? OR id LIKE ?", (f"%{search_query}%", f"%{search_query}%"))
        search_results = cursor.fetchall()
        
        if search_results:
            part_options = {f"{row[1]} (Stock: {row[3]} pcs) - ₹{row[2]}": row for row in search_results}
            selected_option = st.selectbox("Select Matching Part", list(part_options.keys()))
            chosen_row = part_options[selected_option]
            
            qty = st.number_input("Quantity", min_value=1, max_value=max(1, chosen_row[3]), value=1)
            
            if st.button("➕ Add to Cart"):
                item_total = chosen_row[2] * qty
                st.session_state.cart.append({
                    "id": chosen_row[0],
                    "name": chosen_row[1],
                    "price": chosen_row[2],
                    "qty": qty,
                    "total": item_total
                })
                st.success(f"Added {chosen_row[1]} to bill!")
                st.rerun()
        else:
            st.warning("❌ No parts found matching your keyword.")

    # Display Cart / Live Preview
    if st.session_state.cart:
        st.markdown("---")
        st.markdown("### 📋 Current Cart Items")
        parts_total_sum = 0.0
        
        for idx, item in enumerate(st.session_state.cart):
            parts_total_sum += item['total']
            col_i1, col_i2, col_i3 = st.columns([3, 2, 1])
            with col_i1:
                st.write(f"**{item['name']}** (x{item['qty']})")
            with col_i2:
                st.write(f"₹{item['total']:.2f}")
            with col_i3:
                if st.button("❌", key=f"del_cart_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                    
        st.markdown(f"**📦 Parts Total:** ₹{parts_total_sum:.2f}")
        
        st.markdown("---")
        labour_desc = st.text_input("Labour/Fitting Work Description", placeholder="उदा. ब्रेक सर्विस & फिटिंग")
        labour_cost = st.number_input("Labour Charges (₹)", min_value=0.0, step=10.0)
        
        total_bill = parts_total_sum + labour_cost
        
        st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid #fbbf24; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h3 style="color: #fbbf24; margin: 0;">💥 Total Bill Amount: ₹{total_bill:.2f}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        pay_mode = st.selectbox("Payment Mode", ["Cash", "Online/UPI", "Udhar (Credit)"])
        amount_paid = st.number_input("Amount Paid / Advance (₹)", min_value=0.0, max_value=float(total_bill), value=float(total_bill))
        balance_due = max(0.0, total_bill - amount_paid)
        
        if st.button("💾 Save & Generate Estimate Slip"):
            if not c_name or not v_number:
                st.warning("⚠️ Please enter Customer Name and Vehicle Number.")
            else:
                current_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
                items_json = json.dumps(st.session_state.cart)
                
                cursor.execute('''
                    INSERT INTO sales (customer_name, customer_mobile, vehicle_number, vehicle_model, items_summary, parts_total, labour_desc, labour_cost, total_bill, amount_paid, balance_due, payment_mode, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (c_name, c_mobile, v_number, v_model, items_json, parts_total_sum, labour_desc, labour_cost, total_bill, amount_paid, balance_due, pay_mode, current_date))
                
                sale_id = cursor.lastrowid
                
                # Reduce Stock
                for item in st.session_state.cart:
                    cursor.execute("UPDATE parts SET stock = stock - ? WHERE id = ?", (item['qty'], item['id']))
                conn.commit()
                
                st.success(f"✅ Estimate Saved Successfully! ID: #{sale_id}")
                
                # WhatsApp Formatted Message
                formatted_items = "\n".join([f"{idx+1}. {item['name']} (x{item['qty']}) = ₹{item['total']:.2f}" for idx, item in enumerate(st.session_state.cart)])
                
                slip_text = f"""🏎️ *MY SHIVSHAKTI AUTO PARTS & SERVICE*
📍 Main Road, Rantham, Chikhli, Malkapur (MH)
📞 9158551896
-----------------------------------
👤 *Customer:* {c_name}
🚗 *Vehicle:* {v_model} [{v_number}]
📅 *Date:* {current_date}
-----------------------------------
🔧 *Parts List:*
{formatted_items}
-----------------------------------
📦 Parts Total: ₹{parts_total_sum:.2f}
👨‍🔧 Labour ({labour_desc if labour_desc else 'Service'}): ₹{labour_cost:.2f}
-----------------------------------
💰 *Total Bill:* ₹{total_bill:.2f}
✅ *Paid Amount:* ₹{amount_paid:.2f}
🔴 *Pending Udhar:* ₹{balance_due:.2f}
-----------------------------------
🙏 *धन्यवाद! फिर पधारें।*"""

                clean_mobile = c_mobile.replace("+", "").replace(" ", "")
                if len(clean_mobile) == 10:
                    clean_mobile = "91" + clean_mobile
                
                wa_link = f"https://wa.me/{clean_mobile}?text={urllib.parse.quote(slip_text)}"
                st.link_button("📲 Share Slip on WhatsApp", wa_link)
                
                if st.button("🔄 Clear Cart for Next Bill"):
                    st.session_state.cart = []
                    st.rerun()

# --------------------------------------------------------
# TAB 2: INVENTORY STOCK MANAGEMENT
# --------------------------------------------------------
with tab2:
    st.subheader("📦 Inventory Stock Management")
    
    with st.form("add_stock_form", clear_on_submit=True):
        st.markdown("### Add / Update Spare Part")
        p_id = st.text_input("Part ID (e.g. 107)")
        p_name = st.text_input("Part Name")
        p_price = st.number_input("Selling Price (₹)", min_value=0.0, step=10.0)
        p_stock = st.number_input("Stock Quantity", min_value=0, value=10)
        
        submitted = st.form_submit_button("Save to Stock")
        if submitted:
            if p_id and p_name:
                cursor.execute("INSERT OR REPLACE INTO parts VALUES (?, ?, ?, ?)", (p_id, p_name, p_price, p_stock))
                conn.commit()
                st.success("✅ Part added/updated successfully!")
                st.rerun()
            else:
                st.warning("Please fill Part ID and Name.")
                
    st.markdown("### Current Stock List")
    stock_df = pd.read_sql("SELECT * FROM parts", conn)
    if not stock_df.empty:
        st.dataframe(stock_df, use_container_width=True)
    else:
        st.info("No parts found in stock.")

# --------------------------------------------------------
# TAB 3: UDHAR KHATA MANAGEMENT
# --------------------------------------------------------
with tab3:
    st.subheader("📖 Udhar Khata (Pending Dues)")
    
    udhar_df = pd.read_sql("SELECT id, customer_name, customer_mobile, vehicle_number, total_bill, amount_paid, balance_due, date FROM sales WHERE balance_due > 0", conn)
    
    if not udhar_df.empty:
        st.dataframe(udhar_df, use_container_width=True)
        
        st.markdown("### Clear or Pay Udhar")
        pay_id = st.number_input("Enter Estimate ID to Clear Due", min_value=1, step=1)
        pay_amt = st.number_input("Amount Paying Now (₹)", min_value=0.0, step=10.0)
        
        if st.button("Confirm Payment Receipt"):
            cursor.execute("SELECT balance_due, amount_paid FROM sales WHERE id=?", (pay_id,))
            row = cursor.fetchone()
            if row:
                current_due = row[0]
                current_paid = row[1]
                
                if pay_amt > current_due:
                    st.warning(f"Payment cannot exceed remaining due: ₹{current_due:.2f}")
                else:
                    new_paid = current_paid + pay_amt
                    new_due = current_due - pay_amt
                    cursor.execute("UPDATE sales SET amount_paid=?, balance_due=? WHERE id=?", (new_paid, new_due, pay_id))
                    conn.commit()
                    st.success(f"✅ Payment recorded! Remaining due: ₹{new_due:.2f}")
                    st.rerun()
            else:
                st.error("Invalid Estimate ID.")
    else:
        st.info("🎉 शानदार! कोई भी उधार बकाया नहीं है। सभी खाते चुकता हैं।")

# --------------------------------------------------------
# TAB 4: HISTORICAL RECORDS
# --------------------------------------------------------
with tab4:
    st.subheader("📊 All Sales & Estimate Records")
    records_df = pd.read_sql("SELECT id, customer_name, vehicle_number, total_bill, amount_paid, balance_due, payment_mode, date FROM sales ORDER BY id DESC", conn)
    if not records_df.empty:
        st.dataframe(records_df, use_container_width=True)
    else:
        st.info("No sales records found.")
        
