import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse
import base64

# 🎨 Page Configuration (Mobile & Desktop Optimized)
st.set_page_config(
    page_title="My Shivshakti Auto Parts & Service",
    layout="wide",
    page_icon="🏍️"
)

# 🌟 Clean, Proportional & Touch-Friendly CSS (Larger Fonts)
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
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
        padding: 18px 12px;
        margin-bottom: 15px;
        text-align: center;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }
    .top-title {
        color: #d97706;
        font-size: 22px;
        font-weight: 900;
        text-transform: uppercase;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .top-sub {
        color: #334155;
        font-size: 14px;
        margin-top: 6px;
        font-weight: 700;
    }

    .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 2px solid #94a3b8 !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    
    label, .stMarkdown p, span {
        color: #1e293b !important;
        font-size: 15px !important;
        font-weight: 700 !important;
    }

    .stButton>button, .stFormSubmitButton>button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        width: 100%;
        padding: 10px 4px;
        font-size: 15px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# DATABASE SETUP (v13 to fix schema mismatch)
# --------------------------------------------------------
conn = sqlite3.connect("autoparts_shop_v13.db", check_same_thread=False)
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
        extra_desc TEXT,
        extra_cost REAL,
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
        <p class="top-title">🏍️ MY SHIVSHAKTI AUTO PARTS & SERVICE centre</p>
        <p class="top-sub">📍 Main Road, Rantham, Chikhli, Malkapur (MH) &nbsp;|&nbsp;
        OWNER -MR ADITYA YUVRAJ CHIMKAR 📞 9158551896</p>
    </div>
""", unsafe_allow_html=True)

if "menu_tab" not in st.session_state:
    st.session_state.menu_tab = "🛒 Billing"

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
    st.markdown("### ➕ Add Spare Parts")
    
    inv_df = pd.read_sql("SELECT * FROM parts", conn)
    
    inventory_dict = {}
    item_choices = ["-- Custom Item (मैन्युअल लिखें) --"]
    if not inv_df.empty:
        for _, row in inv_df.iterrows():
            item_name = row['name']
            item_choices.append(item_name)
            inventory_dict[item_name] = {
                "mrp": float(row['mrp']),
                "selling_price": float(row['selling_price']),
                "stock": int(row['stock'])
            }

    def update_item_fields():
        selected = st.session_state[f"sel_item_{st.session_state.form_gen}"]
        if selected != "-- Custom Item (मैन्युअल लिखें) --" and selected in inventory_dict:
            st.session_state[f"p_name_{st.session_state.form_gen}"] = selected
            st.session_state[f"p_mrp_{st.session_state.form_gen}"] = inventory_dict[selected]["mrp"]
            st.session_state[f"p_sell_{st.session_state.form_gen}"] = inventory_dict[selected]["selling_price"]
        else:
            st.session_state[f"p_name_{st.session_state.form_gen}"] = ""
            st.session_state[f"p_mrp_{st.session_state.form_gen}"] = 0.0
            st.session_state[f"p_sell_{st.session_state.form_gen}"] = 0.0

    selected_inv_item = st.selectbox("Select Part from Inventory", item_choices, key=f"sel_item_{st.session_state.form_gen}", on_change=update_item_fields)

    if f"p_name_{st.session_state.form_gen}" not in st.session_state:
        st.session_state[f"p_name_{st.session_state.form_gen}"] = ""
    if f"p_mrp_{st.session_state.form_gen}" not in st.session_state:
        st.session_state[f"p_mrp_{st.session_state.form_gen}"] = 0.0
    if f"p_sell_{st.session_state.form_gen}" not in st.session_state:
        st.session_state[f"p_sell_{st.session_state.form_gen}"] = 0.0

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        p_name_final = st.text_input("Part Name", key=f"p_name_{st.session_state.form_gen}")
    with col_b:
        item_mrp_input = st.number_input("MRP (₹)", min_value=0.0, step=10.0, key=f"p_mrp_{st.session_state.form_gen}")
    with col_c:
        item_selling_input = st.number_input("Selling Price (₹)", min_value=0.0, step=10.0, key=f"p_sell_{st.session_state.form_gen}")
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

    parts_total_sum = 0.0
    total_mrp_sum = 0.0
    
    if st.session_state.cart:
        st.markdown("---")
        st.markdown("### 📋 Current Bill Cart (सामान सूची)")
        
        for idx, item in enumerate(st.session_state.cart):
            parts_total_sum += item['total']
            total_mrp_sum += item['total_mrp']
            
            col_i1, col_i2, col_i3 = st.columns([4, 2, 1])
            with col_i1:
                st.markdown(f"**{idx+1}. {item['name']}** (x{item['qty']})<br>MRP: ₹{item['mrp']} | Sell: ₹{item['price']}", unsafe_allow_html=True)
            with col_i2:
                st.markdown(f"<br><b>₹{item['total']:.2f}</b>", unsafe_allow_html=True)
            with col_i3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Delete", key=f"del_cart_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                    
        total_savings = max(0.0, total_mrp_sum - parts_total_sum)
        
        st.markdown(f"""
            <div style="background: #dcfce7; border: 1px solid #22c55e; padding: 12px; border-radius: 8px; margin: 12px 0;">
                <span style="color: #166534; font-size: 16px; font-weight: bold;">🎉 Customer Total Savings (MRP Discount): ₹{total_savings:.2f}</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        total_savings = 0.0

    st.markdown("---")
    st.markdown("### 👨‍🔧 Add Labour & Services (लेबर चार्ज और क्वांटिटी)")
    
    if "labour_list" not in st.session_state:
        st.session_state.labour_list = []
        
    col_l1, col_l2, col_l3, col_l4 = st.columns([3, 2, 1, 1])
    with col_l1:
        l_desc_input = st.text_input("Labour Name", placeholder="उदा. Servicing", key=f"l_desc_input_{st.session_state.form_gen}")
    with col_l2:
        l_cost_input = st.number_input("Rate (₹)", min_value=0.0, step=10.0, key=f"l_cost_input_{st.session_state.form_gen}")
    with col_l3:
        l_qty_input = st.number_input("Qty", min_value=1, value=1, key=f"l_qty_input_{st.session_state.form_gen}")
    with col_l4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add"):
            if l_desc_input and l_cost_input > 0:
                total_l_amt = l_cost_input * l_qty_input
                st.session_state.labour_list.append({
                    "desc": l_desc_input,
                    "cost": l_cost_input,
                    "qty": l_qty_input,
                    "total": total_l_amt
                })
                st.success("Labour added!")
                st.rerun()
            else:
                st.warning("लेबर का नाम और सही कीमत दर्ज करें!")
                
    total_labour_cost = 0.0
    labour_desc_summary = []
    if st.session_state.labour_list:
        for l_idx, lab in enumerate(st.session_state.labour_list):
            total_labour_cost += lab['total']
            labour_desc_summary.append(f"{lab['desc']} (x{lab['qty']}) = ₹{lab['total']}")
            
            cl1, cl2 = st.columns([5, 1])
            with cl1:
                st.write(f"👉 **{lab['desc']}** (Qty: {lab['qty']}) - ₹{lab['cost']} each = ₹{lab['total']:.2f}")
            with cl2:
                if st.button("🗑️", key=f"del_lab_{l_idx}"):
                    st.session_state.labour_list.pop(l_idx)
                    st.rerun()

    # --------------------------------------------------------
    # ADDITIONAL EXTRA WORK / CHARGES SECTION WITH QTY
    # --------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🛠️ Additional Extra Works / Other Charges (अन्य काम और क्वांटिटी)")
    
    if "extra_list" not in st.session_state:
        st.session_state.extra_list = []
        
    col_e1, col_e2, col_e3, col_e4 = st.columns([3, 2, 1, 1])
    with col_e1:
        e_desc_input = st.text_input("Extra Work Name", placeholder="उदा. Welding", key=f"e_desc_input_{st.session_state.form_gen}")
    with col_e2:
        e_cost_input = st.number_input("Rate (₹)", min_value=0.0, step=10.0, key=f"e_cost_input_{st.session_state.form_gen}")
    with col_e3:
        e_qty_input = st.number_input("Qty", min_value=1, value=1, key=f"e_qty_input_{st.session_state.form_gen}")
    with col_e4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Ext"):
            if e_desc_input and e_cost_input > 0:
                total_e_amt = e_cost_input * e_qty_input
                st.session_state.extra_list.append({
                    "desc": e_desc_input,
                    "cost": e_cost_input,
                    "qty": e_qty_input,
                    "total": total_e_amt
                })
                st.success("Extra work added!")
                st.rerun()
            else:
                st.warning("एक्स्ट्रा काम का नाम और सही कीमत दर्ज करें!")

    total_extra_cost = 0.0
    extra_desc_summary = []
    if st.session_state.extra_list:
        for e_idx, ext in enumerate(st.session_state.extra_list):
            total_extra_cost += ext['total']
            extra_desc_summary.append(f"{ext['desc']} (x{ext['qty']}) = ₹{ext['total']}")
            
            cel1, cel2 = st.columns([5, 1])
            with cel1:
                st.write(f"👉 **{ext['desc']}** (Qty: {ext['qty']}) - ₹{ext['cost']} each = ₹{ext['total']:.2f}")
            with cel2:
                if st.button("🗑️", key=f"del_ext_{e_idx}"):
                    st.session_state.extra_list.pop(e_idx)
                    st.rerun()

    # Final Calculation
    total_bill = parts_total_sum + total_labour_cost + total_extra_cost
    
    st.markdown(f"""
        <div style="background: #fef3c7; border: 2px solid #f59e0b; padding: 18px; border-radius: 12px; margin: 15px 0; text-align: center;">
            <h2 style="color: #b45309; margin: 0; font-size: 24px;">💥 Final Bill Amount: ₹{total_bill:.2f}</h2>
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
            for lab in st.session_state.labour_list:
                items_desc_list.append(f"Labour: {lab['desc']} (x{lab['qty']}) - ₹{lab['total']}")
            for ext in st.session_state.extra_list:
                items_desc_list.append(f"Extra: {ext['desc']} (x{ext['qty']}) - ₹{ext['total']}")
            items_summary_str = ", ".join(items_desc_list)
            
            labour_final_desc_str = ", ".join(labour_desc_summary)
            extra_final_desc_str = ", ".join(extra_desc_summary)
            
            cursor.execute('''
                INSERT INTO sales (customer_name, customer_mobile, vehicle_number, vehicle_model, items_summary, parts_total, total_mrp_sum, total_savings, labour_desc, labour_cost, extra_desc, extra_cost, total_bill, amount_paid, balance_due, payment_mode, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (c_name, c_mobile, v_number, v_model, items_summary_str, parts_total_sum, total_mrp_sum, total_savings, labour_final_desc_str, total_labour_cost, extra_final_desc_str, total_extra_cost, total_bill, amount_paid, balance_due, pay_mode, current_date))
            
            sale_id = cursor.lastrowid

            for item in st.session_state.cart:
                cursor.execute("UPDATE parts SET stock = stock - ? WHERE name = ?", (item['qty'], item['name']))

            conn.commit()
            st.success(f"✅ बिल सफलतापूर्वक सेव हो गया! ID: #{sale_id}")
            
    # 📲 WhatsApp & Download PDF Section
    formatted_items = "\n".join([f"{idx+1}. {item['name']} (x{item['qty']}) = ₹{item['total']:.2f}" for idx, item in enumerate(st.session_state.cart)])
    formatted_labour = "\n".join([f"• {lab['desc']} (x{lab['qty']}): ₹{lab['total']:.2f}" for lab in st.session_state.labour_list]) if st.session_state.labour_list else "None"
    formatted_extra = "\n".join([f"• {ext['desc']} (x{ext['qty']}): ₹{ext['total']:.2f}" for ext in st.session_state.extra_list]) if st.session_state.extra_list else "None"
    
    slip_text = f"""🏍️ *MY SHIVSHAKTI AUTO PARTS & SERVICE centre*
📍 Main Road, Rantham, Chikhli, Malkapur (MH)
OWNER NAME- ADITYA YUVRAJ CHIMKAR 📞 9158551896
-----------------------------------
👤 *Customer:* {c_name}
🏍️ *Vehicle:* {v_model} [{v_number}]
📅 *Date:* {datetime.now().strftime("%d-%m-%Y %I:%M %p")}
-----------------------------------
🔧 *Parts List:*
{formatted_items}
-----------------------------------
👨‍🔧 *Labour/Services:*
{formatted_labour}
-----------------------------------
🛠️ *Extra Works:*
{formatted_extra}
-----------------------------------
📦 Parts Total: ₹{parts_total_sum:.2f}
👨‍🔧 Labour Total: ₹{total_labour_cost:.2f}
🛠️ Extra Work Total: ₹{total_extra_cost:.2f}
🎉 *Total Discount (Savings):* ₹{total_savings:.2f}
-----------------------------------
💰 *Total Bill:* ₹{total_bill:.2f}
✅ *Paid:* ₹{amount_paid:.2f}
🔴 *Pending:* ₹{balance_due:.2f}
-----------------------------------
🙏 *धन्यवाद! फिर पधारें।*"""

    st.markdown("### 📤 Share Estimate & Download PDF")
    clean_mobile = c_mobile.replace("+", "").replace(" ", "")
    if len(clean_mobile) == 10:
        clean_mobile = "91" + clean_mobile
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        wa_link = f"https://wa.me/{clean_mobile}?text={urllib.parse.quote(slip_text)}"
        st.link_button("📲 Share via WhatsApp", wa_link)
        
    with col_s2:
        items_html = "".join([f"<tr><td>{itm['name']}</td><td style='text-align:center;'>{itm['qty']}</td><td style='text-align:right;'>₹{itm['total']:.2f}</td></tr>" for itm in st.session_state.cart])
        labour_html = "".join([f"<tr><td colspan='2'>{lab['desc']} (x{lab['qty']})</td><td style='text-align:right;'>₹{lab['total']:.2f}</td></tr>" for lab in st.session_state.labour_list])
        extra_html = "".join([f"<tr><td colspan='2'>{ext['desc']} (x{ext['qty']})</td><td style='text-align:right;'>₹{ext['total']:.2f}</td></tr>" for ext in st.session_state.extra_list])
        
        print_html = f"""
            <html>
            <head><meta charset="utf-8"></head>
            <body style="font-family: Arial; padding: 20px; color: #000;">
                <h2 style="text-align:center; color:#d97706; margin-bottom:0;">MY SHIVSHAKTI AUTO PARTS & SERVICE</h2>
                <p style="text-align:center; margin-top:5px; font-size:12px;">Main Road, Rantham, Chikhli, Malkapur (MH) | Ph: 9158551896</p>
                <hr>
                <p><b>Customer:</b> {c_name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Vehicle:</b> {v_number}</p>
                <p><b>Date:</b> {datetime.now().strftime('%d-%m-%Y %I:%M %p')}</p>
                <table border="1" style="width:100%; border-collapse:collapse; margin-top:10px;" cellpadding="8">
                    <tr style="background:#f1f5f9;"><th>Item Name</th><th style="text-align:center;">Qty</th><th style="text-align:right;">Total (₹)</th></tr>
                    {items_html}
                    {labour_html}
                    {extra_html}
                </table>
                <p style="margin-top:10px; color:#166534; font-weight:bold;">🎉 Customer Total Discount (Savings): ₹{total_savings:.2f}</p>
                <h2 style="color:#b45309; text-align:right;">Final Bill Amount: ₹{total_bill:.2f}</h2>
                <p style="text-align:center; margin-top:30px;"><b>धन्यवाद! फिर पधारें।</b></p>
            </body>
            </html>
        """
        b64 = base64.b64encode(print_html.encode('utf-8')).decode('utf-8')
        pdf_download_link = f'<a href="data:text/html;base64,{b64}" download="Bill_{c_name}_{v_number}.html" target="_blank"><button style="background:linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color:white; border:none; border-radius:10px; padding:12px; width:100%; font-weight:800; cursor:pointer; font-size:16px;">📥 Download Bill / PDF File</button></a>'
        st.markdown(pdf_download_link, unsafe_allow_html=True)
    
    if st.button("🔄 Create New Bill (Reset Cart)"):
        st.session_state.cart = []
        st.session_state.labour_list = []
        st.session_state.extra_list = []
        st.session_state.form_gen += 1
        st.rerun()

# --------------------------------------------------------
# TAB 2: INVENTORY STOCK MANAGEMENT
# --------------------------------------------------------
if st.session_state.menu_tab == "📦 Stock":
    st.subheader("📦 Inventory Stock Management")
    
    # 1. नया पार्ट जोड़ने का फॉर्म
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
                
    st.markdown("---")
    st.markdown("### Current Stock List")
    
    stock_df = pd.read_sql("SELECT * FROM parts", conn)
    if not stock_df.empty:
        # ⚠️ Low Stock Alert (मान लीजिए स्टॉक 5 या उससे कम होने पर लो स्टॉक है)
        LOW_STOCK_LIMIT = 5
        low_stock_df = stock_df[stock_df['stock'] <= LOW_STOCK_LIMIT]
        
        if not low_stock_df.empty:
            st.warning(f"⚠️ चेतावनी: {len(high_alert := low_stock_df)} आइटम का स्टॉक बहुत कम हो गया है!")
            
            # Low Stock Order Generate करने का बटन
            if st.button("📋 Generate Low Stock Order List"):
                st.markdown("#### 🛒 Reorder List (खरीदने के लिए लिस्ट)")
                order_text = "निम्न स्पेयर पार्ट्स का स्टॉक खत्म होने वाला है, कृपया इन्हें जल्द मंगवाएं:\n\n"
                for index, row in low_stock_df.iterrows():
                    order_text += f"- {row['name']} (मौजूदा स्टॉक: {row['stock']})\n"
                
                st.text_area("Copy Order Text / WhatsApp Share:", value=order_text, height=150)
        
        # डेटाफ्रेम दिखाना (लो स्टॉक वाले आइटम्स को हाईलाइट करने के लिए आइकॉन या कंडीशनल फॉर्मेटिंग)
        st.dataframe(stock_df, use_container_width=True)
        
        st.markdown("### Update or Delete Part")
        selected_part = st.selectbox("पार्ट चुनें (संपादित या हटाने के लिए)", stock_df['name'].tolist())
        
        part_data = stock_df[stock_df['name'] == selected_part].iloc[0]
        part_id = part_data['id'] # (ध्यान दें: आपके डेटाबेस टेबल में 'id' कॉलम होना चाहिए)
        
        with st.form("update_delete_form"):
            up_name = st.text_input("Part Name", value=part_data['name'])
            up_mrp = st.number_input("MRP (₹)", min_value=0.0, value=float(part_data['mrp']), step=10.0)
            up_price = st.number_input("Selling Price (₹)", min_value=0.0, value=float(part_data['selling_price']), step=10.0)
            up_stock = st.number_input("Stock Quantity", min_value=0, value=int(part_data['stock']))
            
            col1, col2 = st.columns(2)
            with col1:
                update_btn = st.form_submit_button("🔄 Update Stock")
            with col2:
                delete_btn = st.form_submit_button("🗑️ Delete Part")
                
            if update_btn:
                cursor.execute("""
                    UPDATE parts 
                    SET name = ?, mrp = ?, selling_price = ?, stock = ? 
                    WHERE id = ?
                """, (up_name, up_mrp, up_price, up_stock, part_id))
                conn.commit()
                st.success("✅ स्टॉक सफलतापूर्वक अपडेट हो गया!")
                st.rerun()
                
            if delete_btn:
                cursor.execute("DELETE FROM parts WHERE id = ?", (part_id,))
                conn.commit()
                st.error("🗑️ पार्ट को स्टॉक से हटा दिया गया है!")
                st.rerun()
    else:
        st.info("स्टॉक में कोई सामान उपलब्ध नहीं है।")

# --------------------------------------------------------
# TAB 3: UDHAR KHATA MANAGEMENT
# --------------------------------------------------------
elif st.session_state.menu_tab == "📖 Udhar":
    st.subheader("📖 Udhar Khata (Pending Dues)")
    udhar_df = pd.read_sql("SELECT id, customer_name, vehicle_number, total_bill, amount_paid, balance_due, date FROM sales WHERE balance_due > 0 ORDER BY id DESC", conn)
    
    if not udhar_df.empty:
        st.dataframe(udhar_df, use_container_width=True)
        
        st.markdown("### 💰 Clear / Receive Due Payment")
        due_id = st.number_input("Enter Bill / Sale ID to Clear Due", min_value=1, step=1)
        paying_amt = st.number_input("Amount Being Paid Now (₹)", min_value=0.0, step=10.0)
        
        if st.button("✅ Update Udhar Payment"):
            cursor.execute("SELECT balance_due, amount_paid FROM sales WHERE id = ?", (due_id,))
            record = cursor.fetchone()
            if record:
                current_due = record[0]
                current_paid = record[1]
                
                new_paid = current_paid + paying_amt
                new_due = max(0.0, current_due - paying_amt)
                
                cursor.execute("UPDATE sales SET amount_paid = ?, balance_due = ? WHERE id = ?", (new_paid, new_due, due_id))
                conn.commit()
                st.success(f"✅ बिल ID #{due_id} का पेमेंट अपडेट हो गया! नया बकाया: ₹{new_due:.2f}")
                st.rerun()
            else:
                st.warning("⚠️ यह Bill ID नहीं मिली। सही ID दर्ज करें।")
    else:
        st.info("🎉 बहुत बढ़िया! कोई भी उधार/पेंडिंग बकाया नहीं है।")

# --------------------------------------------------------
# TAB 4: SALES RECORDS
# --------------------------------------------------------
elif st.session_state.menu_tab == "📊 Records":
    st.subheader("📊 Complete Sales Records & History")
    
    records_df = pd.read_sql("SELECT * FROM sales ORDER BY id DESC", conn)
    if not records_df.empty:
        st.dataframe(records_df, use_container_width=True)
        
        total_revenue = records_df['amount_paid'].sum()
        total_pending = records_df['balance_due'].sum()
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("💵 Total Revenue Collected", f"₹{total_revenue:.2f}")
        with col_r2:
            st.metric("🔴 Total Pending Market Dues", f"₹{total_pending:.2f}")
    else:
        st.info("अभी तक कोई बिक्री रिकॉर्ड दर्ज नहीं हुआ है।")
