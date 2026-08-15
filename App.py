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
    .stApp {
        background: radial-gradient(circle at top left, #1e293b, #0f172a, #020617);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .hero-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(245, 158, 11, 0.4);
        box-shadow: 0 10px 30px -10px rgba(245, 158, 11, 0.3);
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
        margin: 0;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 13px;
        margin-top: 5px;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #0f172a !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
        width: 100%;
        padding: 10px;
    }
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
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706) !important;
        color: #0f172a !important;
        font-weight: 800 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------------
conn = sqlite3.connect("autoparts_shop_v4.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mrp REAL,
        selling_price REAL,
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
        total_mrp_sum REAL,
        total_savings REAL,
        labour_desc TEXT,
        labour_cost REAL,
        total_bill REAL,
        amount_paid REAL,
        balance_due REAL,
        payment_mode TEXT,
        date TEXT
    )
''')
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

tab1, tab2, tab3, tab4 = st.tabs(["🛒 Estimate & Billing", "📦 Inventory Stock", "📖 Udhar Khata", "📊 Records"])

# --------------------------------------------------------
# TAB 1: ESTIMATE & BILLING (AUTO MRP / SELLING PRICE)
# --------------------------------------------------------
with tab1:
    st.subheader("📝 New Customer Estimate & Billing")
    
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
    st.markdown("### ➕ Add Items (Auto-fetch MRP & Selling Price)")
    
    # Fetch inventory data
    inv_df = pd.read_sql("SELECT * FROM parts", conn)
    
    # Dictionary creation for quick auto-fill lookup
    inventory_dict = {}
    item_choices = ["-- Custom Item (मैन्युअल लिखें) --"]
    if not inv_df.empty:
        for _, row in inv_df.iterrows():
            item_name = row['name']
            item_choices.append(item_name)
            inventory_dict[item_name] = {
                "mrp": row['mrp'],
                "selling_price": row['selling_price']
            }

    selected_inv_item = st.selectbox("Select Part from Inventory", item_choices)

    # Automatic default values setup based on selection
    default_mrp = 0.0
    default_selling = 0.0
    if selected_inv_item != "-- Custom Item (मैन्युअल लिखें) --" and selected_inv_item in inventory_dict:
        default_mrp = float(inventory_dict[selected_inv_item]["mrp"])
        default_selling = float(inventory_dict[selected_inv_item]["selling_price"])

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        # If inventory item selected, use it as default name; else allow custom typing
        if selected_inv_item != "-- Custom Item (मैन्युअल लिखें) --":
            p_name_final = st.text_input("Part Name", value=selected_inv_item)
        else:
            p_name_final = st.text_input("Custom Part Name", placeholder="उदा. Chain Cleaning")
    with col_b:
        item_mrp_input = st.number_input("MRP (₹)", min_value=0.0, value=default_mrp, step=10.0)
    with col_c:
        item_selling_input = st.number_input("Selling Price (₹)", min_value=0.0, value=default_selling, step=10.0)
    with col_d:
        qty_input = st.number_input("Quantity", min_value=1, value=1)

    if st.button("➕ Add to Bill Cart"):
        if p_name_final and item_selling_input > 0:
            final_mrp = item_mrp_input if item_mrp_input > 0 else item_selling_input
            item_total = item_selling_input * qty_input
            item_total_mrp = final_mrp * qty_input
            
            st.session_state.cart.append({
                "name": p_name_final,
                "mrp": final_mrp,
                "price": item_selling_input,
                "qty": qty_input,
                "total": item_total,
                "total_mrp": item_total_mrp
            })
            st.success(f"Added {p_name_final} to cart!")
            st.rerun()
        else:
            st.warning("⚠️ कृपया सही पार्ट का नाम और सेलिंग प्राइस दर्ज करें!")

    # Display Cart / Live Preview
    if st.session_state.cart:
        st.markdown("---")
        st.markdown("### 📋 Current Bill Cart")
        parts_total_sum = 0.0
        total_mrp_sum = 0.0
        
        for idx, item in enumerate(st.session_state.cart):
            parts_total_sum += item['total']
            total_mrp_sum += item['total_mrp']
            
            col_i1, col_i2, col_i3 = st.columns([3, 2, 1])
            with col_i1:
                st.write(f"**{item['name']}** (x{item['qty']}) | MRP: ₹{item['mrp']} | Sell: ₹{item['price']}")
            with col_i2:
                st.write(f"₹{item['total']:.2f}")
            with col_i3:
                if st.button("❌", key=f"del_cart_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                    
        total_savings = max(0.0, total_mrp_sum - parts_total_sum)
        
        st.markdown(f"""
            <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; padding: 10px; border-radius: 8px; margin: 10px 0;">
                <span style="color: #22c55e; font-weight: bold;">🎉 Customer Total Savings (MRP Discount): ₹{total_savings:.2f}</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        labour_desc = st.text_input("Labour / Fitting Work Description", placeholder="उदा. सर्विसिंग और फिटिंग चार्ज")
        labour_cost = st.number_input("Labour Charges (₹)", min_value=0.0, step=10.0)
        
        total_bill = parts_total_sum + labour_cost
        
        st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid #fbbf24; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h3 style="color: #fbbf24; margin: 0;">💥 Final Bill Amount: ₹{total_bill:.2f}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        pay_mode = st.selectbox("Payment Mode", ["Cash", "Online/UPI", "Udhar (Credit)"])
        amount_paid = st.number_input("Amount Paid / Advance (₹)", min_value=0.0, max_value=float(total_bill), value=float(total_bill))
        balance_due = max(0.0, total_bill - amount_paid)
        
        if st.button("💾 Save & Generate Bill Slip"):
            if not c_name or not v_number:
                st.warning("⚠️ कृपया कस्टमर का नाम और गाड़ी नंबर दर्ज करें।")
            else:
                current_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
                
                # Readable summary string for database records & udhar tracking
                items_desc_list = [f"{item['name']} (x{item['qty']})" for item in st.session_state.cart]
                if labour_desc:
                    items_desc_list.append(f"Labour: {labour_desc}")
                items_summary_str = ", ".join(items_desc_list)
                
                cursor.execute('''
                    INSERT INTO sales (customer_name, customer_mobile, vehicle_number, vehicle_model, items_summary, parts_total, total_mrp_sum, total_savings, labour_desc, labour_cost, total_bill, amount_paid, balance_due, payment_mode, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (c_name, c_mobile, v_number, v_model, items_summary_str, parts_total_sum, total_mrp_sum, total_savings, labour_desc, labour_cost, total_bill, amount_paid, balance_due, pay_mode, current_date))
                
                sale_id = cursor.lastrowid
                conn.commit()
                
                st.success(f"✅ बिल सफलतापूर्व सेव हो गया! ID: #{sale_id}")
                
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
🎉 *You Saved:* ₹{total_savings:.2f} (MRP Discount)
-----------------------------------
💰 *Total Bill:* ₹{total_bill:.2f}
✅ *Paid Amount:* ₹{amount_paid:.2f}
🔴 *Pending Udhar:* ₹{balance_due:.2f}
-----------------------------------
🙏 *धन्यवाद! फिर पधारें।*"""

                clean_mobile = c_mobile.replace("+", "").replace(" ", "")
                if len(clean_mobile) == 10:
                    clean_mobile = "91" + clean_mobile
                
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    wa_link = f"https://wa.me/{clean_mobile}?text={urllib.parse.quote(slip_text)}"
                    st.link_button("📲 Share via WhatsApp", wa_link)
                with col_s2:
                    sms_link = f"sms:{c_mobile}?body={urllib.parse.quote(slip_text)}"
                    st.link_button("💬 Share via SMS", sms_link)
                
                if st.button("🔄 Clear Cart for Next Bill"):
                    st.session_state.cart = []
                    st.rerun()

# --------------------------------------------------------
# TAB 2: INVENTORY STOCK MANAGEMENT
# --------------------------------------------------------
with tab2:
    st.subheader("📦 Inventory Stock Management")
    
    with st.form("add_stock_form", clear_on_submit=True):
        st.markdown("### Add New Spare Part")
        p_name = st.text_input("Part Name")
        p_mrp = st.number_input("MRP (₹)", min_value=0.0, step=10.0)
        p_price = st.number_input("Selling Price (₹)", min_value=0.0, step=10.0)
        p_stock = st.number_input("Stock Quantity", min_value=0, value=10)
        
        submitted = st.form_submit_button("Save Part to Stock")
        if submitted:
            if p_name and p_price > 0:
                cursor.execute("INSERT INTO parts (name, mrp, selling_price, stock) VALUES (?, ?, ?, ?)", (p_name, p_mrp, p_price, p_stock))
                conn.commit()
                st.success("✅ पार्ट सफलतापूर्वक स्टॉक में जोड़ दिया गया!")
                st.rerun()
            else:
                st.warning("कृपया पार्ट का नाम और सेलिंग प्राइस दर्ज करें।")
                
    st.markdown("### Current Stock List")
    stock_df = pd.read_sql("SELECT * FROM parts", conn)
    if not stock_df.empty:
        st.dataframe(stock_df, use_container_width=True)
    else:
        st.info("स्टॉक में कोई सामान उपलब्ध नहीं है।")

# --------------------------------------------------------
# TAB 3: UDHAR KHATA MANAGEMENT (WITH WORK DETAILS)
# --------------------------------------------------------
with tab3:
    st.subheader("📖 Udhar Khata (Pending Dues & Work History)")
    
    # Now selecting items_summary so you can see what work was done
    udhar_df = pd.read_sql("SELECT id, customer_name, customer_mobile, vehicle_number, items_summary, total_bill, amount_paid, balance_due, date FROM sales WHERE balance_due > 0", conn)
    
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
                    st.warning(f"भुगतान बकाया राशि से अधिक नहीं हो सकता: ₹{current_due:.2f}")
                else:
                    new_paid = current_paid + pay_amt
                    new_due = current_due - pay_amt
                    cursor.execute("UPDATE sales SET amount_paid=?, balance_due=? WHERE id=?", (new_paid, new_due, pay_id))
                    conn.commit()
                    st.success(f"✅ भुगतान दर्ज हो गया! नया बकाया: ₹{new_due:.2f}")
                    st.rerun()
            else:
                st.error("अमान्य एस्टीमेट ID!")
    else:
        st.info("🎉 शानदार! कोई भी उधार बकाया नहीं है।")

# --------------------------------------------------------
# TAB 4: HISTORICAL RECORDS (WITH WORK DETAILS)
# --------------------------------------------------------
with tab4:
    st.subheader("📊 All Sales & Service Records")
    # Now selecting items_summary here too so complete history of work done is visible
    records_df = pd.read_sql("SELECT id, customer_name, vehicle_number, items_summary, total_bill, amount_paid, balance_due, total_savings, payment_mode, date FROM sales ORDER BY id DESC", conn)
    if not records_df.empty:
        st.dataframe(records_df, use_container_width=True)
    else:
        st.info("कोई पुराना रिकॉर्ड नहीं मिला।")
            
