import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# 🎨 Page Configuration (Mobile & Desktop Optimized)
st.set_page_config(
    page_title="My Shivshakti Auto Parts & Service",
    layout="wide",
    page_icon="🏎️"
)

# 🌟 Advanced UI Styling for Clear Visibility
st.markdown("""
    <style>
    .stApp {
        background: #f8fafc;
        color: #0f172a;
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .top-header {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        border: 2px solid #cbd5e1;
        border-bottom: 4px solid #f59e0b;
        padding: 18px 10px;
        margin-bottom: 15px;
        text-align: center;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .top-title {
        color: #d97706;
        font-size: 21px;
        font-weight: 900;
        text-transform: uppercase;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .top-sub {
        color: #334155;
        font-size: 13px;
        margin-top: 6px;
        font-weight: 700;
    }

    .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        border: 1.5px solid #94a3b8 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }
    
    label, .stMarkdown p, span {
        color: #1e293b !important;
        font-weight: 600;
    }

    .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #94a3b8 !important;
        border-radius: 8px !important;
    }

    .stButton>button, .stFormSubmitButton>button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 900 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
        width: 100%;
        padding: 10px 2px;
        font-size: 13px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------------
conn = sqlite3.connect("autoparts_shop_v12.db", check_same_thread=False)
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
# UI TOP HEADER
# --------------------------------------------------------
st.markdown("""
    <div class="top-header">
        <p class="top-title">🏎️ MY SHIVSHAKTI AUTO PARTS & SERVICE</p>
        <p class="top-sub">📍 Main Road, Rantham, Chikhli, Malkapur (MH) &nbsp;|&nbsp; 📞 9158551896</p>
    </div>
""", unsafe_allow_html=True)

# 🌟 Session State for Menu Selection
if "menu_tab" not in st.session_state:
    st.session_state.menu_tab = "🛒 Billing"

# 🌟 Horizontal Navigation Buttons in a Single Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    if st.button("🛒 Billing", key="btn_bill"):
        st.session_state.menu_tab = "🛒 Billing"
        st.rerun()
with m2:
    if st.button("📦 Stock", key="btn_stock"):
        st.session_state.menu_tab = "📦 Stock"
        st.rerun()
with m3:
    if st.button("📖 Udhar", key="btn_udhar"):
        st.session_state.menu_tab = "📖 Udhar"
        st.rerun()
with m4:
    if st.button("📊 Records", key="btn_records"):
        st.session_state.menu_tab = "📊 Records"
        st.rerun()

st.markdown("---")

# --------------------------------------------------------
# TAB 1: ESTIMATE & BILLING
# --------------------------------------------------------
if st.session_state.menu_tab == "🛒 Billing":
    st.subheader("📝 New Customer Estimate & Billing")
    
    if "form_gen" not in st.session_state:
        st.session_state.form_gen = 0

    no_bill_mode = st.checkbox("⚡ Quick Direct Sale (बिना कस्टमर डिटेल के सीधा बिल)", value=False, key=f"nobill_{st.session_state.form_gen}")

    if not no_bill_mode:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            c_name = st.text_input("Customer Name", value="", placeholder="कस्टमर का नाम लिखें...", key=f"c_name_{st.session_state.form_gen}")
            c_mobile = st.text_input("Customer Mobile Number", value="", placeholder="मोबाइल नंबर लिखें...", key=f"c_mobile_{st.session_state.form_gen}")
        with col_c2:
            v_number = st.text_input("Vehicle Number", value="", placeholder="गाड़ी नंबर (उदा. MH19...)", key=f"v_num_{st.session_state.form_gen}").upper()
            v_model = st.text_input("Vehicle Model", value="", placeholder="गाड़ी का मॉडल (उदा. Splendor)", key=f"v_model_{st.session_state.form_gen}")
    else:
        c_name = "Counter Cash Customer"
        c_mobile = ""
        v_number = "NA"
        v_model = "Counter Sale"
        st.info("⚡ क्विक मोड चालू है: कस्टमर डिटेल्स की आवश्यकता नहीं है।")

    if "cart" not in st.session_state:
        st.session_state.cart = []

    st.markdown("---")
    st.markdown("### ➕ Add Items (MRP & Selling Price)")
    
    inv_df = pd.read_sql("SELECT * FROM parts", conn)
    
    inventory_dict = {}
    item_choices = ["-- Custom Item (मैन्युअल लिखें) --"]
    if not inv_df.empty:
        for _, row in inv_df.iterrows():
            item_name = row['name']
            item_choices.append(item_name)
            inventory_dict[item_name] = {
                "mrp": row['mrp'],
                "selling_price": row['selling_price'],
                "stock": row['stock']
            }

    selected_inv_item = st.selectbox("Select Part from Inventory", item_choices, key=f"sel_item_{st.session_state.form_gen}")

    default_mrp = 0.0
    default_selling = 0.0
    prefilled_name = ""
    
    if selected_inv_item != "-- Custom Item (मैन्युअल लिखें) --" and selected_inv_item in inventory_dict:
        default_mrp = float(inventory_dict[selected_inv_item]["mrp"])
        default_selling = float(inventory_dict[selected_inv_item]["selling_price"])
        prefilled_name = selected_inv_item

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        p_name_final = st.text_input("Part Name", value=prefilled_name, placeholder="पार्ट का नाम लिखें...", key=f"p_name_{st.session_state.form_gen}")
    with col_b:
        item_mrp_input = st.number_input("MRP (₹)", min_value=0.0, value=default_mrp, step=10.0, key=f"p_mrp_{st.session_state.form_gen}")
    with col_c:
        item_selling_input = st.number_input("Selling Price (₹)", min_value=0.0, value=default_selling, step=10.0, key=f"p_sell_{st.session_state.form_gen}")
    with col_d:
        qty_input = st.number_input("Quantity", min_value=1, value=1, key=f"p_qty_{st.session_state.form_gen}")

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
            <div style="background: #dcfce7; border: 1px solid #22c55e; padding: 10px; border-radius: 8px; margin: 10px 0;">
                <span style="color: #166534; font-weight: bold;">🎉 Customer Total Savings (MRP Discount): ₹{total_savings:.2f}</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        labour_desc = st.text_input("Labour / Fitting Work Description", value="", placeholder="उदा. सर्विसिंग और फिटिंग चार्ज", key=f"lab_desc_{st.session_state.form_gen}")
        labour_cost = st.number_input("Labour Charges (₹)", min_value=0.0, value=0.0, step=10.0, key=f"lab_cost_{st.session_state.form_gen}")
        
        total_bill = parts_total_sum + labour_cost
        
        st.markdown(f"""
            <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h3 style="color: #b45309; margin: 0;">💥 Final Bill Amount: ₹{total_bill:.2f}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        pay_mode = st.selectbox("Payment Mode", ["Cash", "Online/UPI", "Udhar (Credit)"], key=f"pay_mode_{st.session_state.form_gen}")
        amount_paid = st.number_input("Amount Paid / Advance (₹)", min_value=0.0, max_value=float(total_bill), value=float(total_bill), key=f"amt_paid_{st.session_state.form_gen}")
        balance_due = max(0.0, total_bill - amount_paid)
        
        if st.button("💾 Save & Generate Bill Slip"):
            if not no_bill_mode and (not c_name or not v_number):
                st.warning("⚠️ कृपया कस्टमर का नाम और गाड़ी नंबर दर्ज करें।")
            else:
                current_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
                
                items_desc_list = [f"{item['name']} (x{item['qty']})" for item in st.session_state.cart]
                if labour_desc:
                    items_desc_list.append(f"Labour: {labour_desc}")
                items_summary_str = ", ".join(items_desc_list)
                
                cursor.execute('''
                    INSERT INTO sales (customer_name, customer_mobile, vehicle_number, vehicle_model, items_summary, parts_total, total_mrp_sum, total_savings, labour_desc, labour_cost, total_bill, amount_paid, balance_due, payment_mode, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (c_name, c_mobile, v_number, v_model, items_summary_str, parts_total_sum, total_mrp_sum, total_savings, labour_desc, labour_cost, total_bill, amount_paid, balance_due, pay_mode, current_date))
                
                sale_id = cursor.lastrowid

                for item in st.session_state.cart:
                    cursor.execute("UPDATE parts SET stock = stock - ? WHERE name = ?", (item['qty'], item['name']))

                conn.commit()
                st.success(f"✅ बिल सफलतापूर्वक सेव हो गया! ID: #{sale_id}")
                
        # 📲 WhatsApp & Print/PDF Sharing Section
        formatted_items = "\n".join([f"{idx+1}. {item['name']} (x{item['qty']}) = ₹{item['total']:.2f}" for idx, item in enumerate(st.session_state.cart)])
        
        slip_text = f"""🏎️ *MY SHIVSHAKTI AUTO PARTS & SERVICE*
📍 Main Road, Rantham, Chikhli, Malkapur (MH)
📞 9158551896
-----------------------------------
👤 *Customer:* {c_name}
🚗 *Vehicle:* {v_model} [{v_number}]
📅 *Date:* {datetime.now().strftime("%d-%m-%Y %I:%M %p")}
-----------------------------------
🔧 *Parts List:*
{formatted_items}
-----------------------------------
📦 Parts Total: ₹{parts_total_sum:.2f}
👨‍🔧 Labour: ₹{labour_cost:.2f}
🎉 *You Saved:* ₹{total_savings:.2f}
-----------------------------------
💰 *Total Bill:* ₹{total_bill:.2f}
✅ *Paid:* ₹{amount_paid:.2f}
🔴 *Pending:* ₹{balance_due:.2f}
-----------------------------------
🙏 *धन्यवाद! फिर पधारें।*"""

        st.markdown("### 📤 Share Estimate & Print PDF")
        clean_mobile = c_mobile.replace("+", "").replace(" ", "")
        if len(clean_mobile) == 10:
            clean_mobile = "91" + clean_mobile
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            wa_link = f"https://wa.me/{clean_mobile}?text={urllib.parse.quote(slip_text)}"
            st.link_button("📲 Share via WhatsApp", wa_link)
            
        with col_s2:
            items_html = "".join([f"<tr><td>{itm['name']}</td><td style='text-align:center;'>{itm['qty']}</td><td style='text-align:right;'>₹{itm['total']:.2f}</td></tr>" for itm in st.session_state.cart])
            print_html = f"""
                <html>
                <body style="font-family: Arial; padding: 20px;">
                    <h2 style="text-align:center; color:#d97706; margin-bottom:0;">MY SHIVSHAKTI AUTO PARTS & SERVICE</h2>
                    <p style="text-align:center; margin-top:5px;">Main Road, Rantham, Chikhli, Malkapur (MH) | Ph: 9158551896</p>
                    <hr>
                    <p><b>Customer:</b> {c_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Vehicle:</b> {v_number}</p>
                    <p><b>Date:</b> {datetime.now().strftime('%d-%m-%Y %I:%M %p')}</p>
                    <table border="1" style="width:100%; border-collapse:collapse; margin-top:10px;" cellpadding="8">
                        <tr style="background:#f1f5f9;"><th>Item Name</th><th>Qty</th><th>Total (₹)</th></tr>
                        {items_html}
                    </table>
                    <h3>Labour Charges: ₹{labour_cost:.2f}</h3>
                    <h2 style="color:#b45309;">Final Bill Amount: ₹{total_bill:.2f}</h2>
                    <p style="text-align:center; margin-top:30px;"><b>धन्यवाद! फिर पधारें।</b></p>
                    <script>window.print();</script>
                </body>
                </html>
            """
            encoded_html = urllib.parse.quote(print_html)
            st.markdown(f'<a href="data:text/html;charset=utf-8,{encoded_html}" target="_blank"><button style="background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color:white; border:none; border-radius:10px; padding:10px; width:100%; font-weight:900; cursor:pointer;">🖨️ Print / Save PDF Estimate</button></a>', unsafe_allow_html=True)
        
        if st.button("🔄 Create New Bill (Reset Cart)"):
            st.session_state.cart = []
            st.session_state.form_gen += 1
            st.rerun()

# --------------------------------------------------------
# TAB 2: INVENTORY STOCK MANAGEMENT
# --------------------------------------------------------
elif st.session_state.menu_tab == "📦 Stock":
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
# TAB 3: UDHAR KHATA MANAGEMENT
# --------------------------------------------------------
elif st.session_state.menu_tab == "📖 Udhar":
    st.subheader("📖 Udhar Khata (Pending Dues)")
    
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
# TAB 4: HISTORICAL RECORDS
# --------------------------------------------------------
elif st.session_state.menu_tab == "📊 Records":
    st.subheader("📊 All Sales & Service Records")
    records_df = pd.read_sql("SELECT id, customer_name, vehicle_number, items_summary, total_bill, amount_paid, balance_due, total_savings, payment_mode, date FROM sales ORDER BY id DESC", conn)
    if not records_df.empty:
        st.dataframe(records_df, use_container_width=True)
    else:
        st.info("कोई पुराना रिकॉर्ड नहीं मिला।")
                                    
