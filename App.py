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

# Database Connection (v9 नया वर्शन ताकि पुरानी टेबल का कोई एरर न आए)
conn = sqlite3.connect('garage_billing_v9.db', check_same_thread=False)
c = conn.cursor()

# Tables Setup with MRP, Selling Price, and Payment Mode
c.execute('''CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT,
    mrp REAL,
    selling_price REAL,
    stock INTEGER
)''')

c.execute('''CREATE TABLE IF NOT EXISTS bills (
    bill_id TEXT,
    customer_name TEXT,
    phone TEXT,
    vehicle TEXT,
    total REAL,
    udhar REAL,
    payment_mode TEXT,
    date TEXT,
    items TEXT,
    total_savings REAL
)''')
conn.commit()

# Top Header Layout
st.markdown("""
    <div class="header-card">
        <div>
            <p class="header-title">🏎️ Pro Garage ERP</p>
            <p class="header-sub">Mobile Billing & Inventory System</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# App Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📝 Billing", "📦 Inventory", "📊 Records"])

with tab1:
    st.subheader("New Service Bill")
    
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name")
        phone = st.text_input("Phone Number", value="91")
    with col2:
        vehicle_number = st.text_input("Vehicle Number")
        payment_mode = st.selectbox("Payment Mode", ["Cash", "Online/UPI", "Udhar (Credit)"])

    st.markdown("---")
    st.markdown("### Add Items / Services")
    
    # Fetch inventory items
    c.execute("SELECT item_name, mrp, selling_price, stock FROM inventory")
    inventory_items = c.fetchall()
    item_options = {row[0]: {"mrp": row[1], "price": row[2], "stock": row[3]} for row in inventory_items}
    
    if "cart" not in st.session_state:
        st.session_state.cart = []

    with st.form("add_item_form", clear_on_submit=True):
        selected_item = st.selectbox("Select Item/Service", ["-- Custom Item --"] + list(item_options.keys()))
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            custom_name = st.text_input("Custom Item Name")
        with col_b:
            item_mrp = st.number_input("MRP (₹)", min_value=0.0, value=0.0, step=10.0)
        with col_c:
            item_price = st.number_input("Selling Price (₹)", min_value=0.0, value=0.0, step=10.0)
            
        col_d, col_e = st.columns(2)
        with col_d:
            qty = st.number_input("Quantity", min_value=1, value=1)
        with col_e:
            add_btn = st.form_submit_button("Add to Bill")
            
        if add_btn:
            # अगर कस्टम आइटम चुना है और नाम लिखा है, तो वो लें; वरना सिलेक्टेड इन्वेंट्री आइटम लें
            if selected_item == "-- Custom Item --":
                name_to_add = custom_name
                final_mrp = item_mrp
                final_price = item_price
            else:
                name_to_add = selected_item
                final_mrp = item_options.get(selected_item, {}).get("mrp", 0.0)
                final_price = item_options.get(selected_item, {}).get("price", 0.0)
                
            if name_to_add:
                st.session_state.cart.append({
                    "name": name_to_add,
                    "mrp": final_mrp,
                    "price": final_price,
                    "qty": qty
                })
                st.success(f"Added {name_to_add} to bill!")
                st.rerun()
            else:
                st.warning("Please enter or select a valid item name.")

    # Display Cart / Items added
    if st.session_state.cart:
        st.markdown("### Current Bill Items")
        total_amount = 0
        total_mrp_sum = 0
        item_details_list = []
        
        for idx, item in enumerate(st.session_state.cart):
            subtotal = item["price"] * item["qty"]
            sub_mrp = item["mrp"] * item["qty"]
            total_amount += subtotal
            total_mrp_sum += sub_mrp
            
            item_details_list.append(f"- {item['name']} (x{item['qty']}): ₹{subtotal:.2f}")
            
            col_x, col_y, col_z = st.columns([3, 2, 1])
            with col_x:
                st.write(f"**{item['name']}** x {item['qty']}")
            with col_y:
                st.write(f"₹{subtotal:.2f} (MRP: ₹{sub_mrp:.2f})")
            with col_z:
                if st.button("❌", key=f"del_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                    
        total_savings = total_mrp_sum - total_amount
        if total_savings < 0:
            total_savings = 0.0

        udhar_amount = total_amount if payment_mode == "Udhar (Credit)" else 0.0

        st.markdown(f"""
            <div class="stat-card" style="margin-top: 10px;">
                <span style="color: #fbbf24; font-size: 16px; font-weight: bold;">Total: ₹{total_amount:.2f} | Udhar: ₹{udhar_amount:.2f}</span><br>
                <span style="color: #4ade80; font-size: 13px;">🎉 You Saved: ₹{total_savings:.2f} (MRP Discount)</span>
            </div>
        """, unsafe_allow_html=True)

        if st.button("💾 Save Bill & Share WhatsApp"):
            if not customer_name or not vehicle_number:
                st.warning("Please enter Customer Name and Vehicle Number.")
            else:
                bill_id = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
                items_str = ", ".join([f"{i['name']} (x{i['qty']})" for i in st.session_state.cart])
                
                c.execute("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (bill_id, customer_name, phone, vehicle_number, total_amount, udhar_amount, payment_mode, date_str, items_str, total_savings))
                conn.commit()
                
                st.success("✅ Bill Saved Successfully!")
                
                # Create WhatsApp Message with Supermarket-style Savings
                items_text_wa = "\n".join(item_details_list)
                wa_message = f"""🛠️ *PRO GARAGE ERP* 🛠️
📍 Main Road, City
📞 09158551896
----------------------------------------
👤 *Customer:* {customer_name}
🚗 *Vehicle:* {vehicle_number}
📅 *Date:* {date_str}
----------------------------------------
🧾 *Bill Details:*
{items_text_wa}
----------------------------------------
💰 *Total Amount:* ₹{total_amount:.2f}
💳 *Payment Mode:* {payment_mode}
🎉 *You Saved:* ₹{total_savings:.2f} (MRP पर बचत)
----------------------------------------
🙏 Thank you for visiting! Please visit again."""

                encoded_msg = urllib.parse.quote(wa_message)
                whatsapp_url = f"https://wa.me/{phone}?text={encoded_msg}"
                
                st.link_button("📲 Send WhatsApp Bill", whatsapp_url)
                
                if st.button("Clear Cart & Create New Bill"):
                    st.session_state.cart = []
                    st.rerun()

with tab2:
    st.subheader("Manage Inventory")
    with st.form("add_inventory_form", clear_on_submit=True):
        inv_name = st.text_input("Item Name / Spare Part")
        inv_mrp = st.number_input("MRP (₹)", min_value=0.0, step=10.0)
        inv_price = st.number_input("Selling Price (₹)", min_value=0.0, step=10.0)
        inv_stock = st.number_input("Stock Quantity", min_value=0, value=10)
        
        submit_inv = st.form_submit_button("Add to Inventory")
        if submit_inv and inv_name:
            c.execute("INSERT INTO inventory (item_name, mrp, selling_price, stock) VALUES (?, ?, ?, ?)",
                      (inv_name, inv_mrp, inv_price, inv_stock))
            conn.commit()
            st.success(f"Added {inv_name} to inventory!")
            st.rerun()
            
    st.markdown("### Current Inventory Stock")
    inv_df = pd.read_sql("SELECT * FROM inventory", conn)
    if not inv_df.empty:
        st.dataframe(inv_df, use_container_width=True)
    else:
        st.info("No items in inventory yet.")

with tab3:
    st.subheader("Saved Bills & Records")
    bills_df = pd.read_sql("SELECT * FROM bills ORDER BY date DESC", conn)
    if not bills_df.empty:
        st.dataframe(bills_df, use_container_width=True)
    else:
        st.info("No bill records found.")
    
