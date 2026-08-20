import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse
import base64

# Page Configuration
st.set_page_config(
    page_title="My Shivshakti Auto Parts & Service",
    layout="wide",
    page_icon="🏎️"
)

# Custom CSS
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
        padding: 16px 10px;
        margin-bottom: 15px;
        text-align: center;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    }
    .top-title {
        color: #d97706;
        font-size: 20px;
        font-weight: 900;
        text-transform: uppercase;
        margin: 0;
    }
    .top-sub {
        color: #334155;
        font-size: 12px;
        margin-top: 5px;
        font-weight: 700;
    }
    .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #94a3b8 !important;
        border-radius: 8px !important;
        padding: 8px 10px !important;
        font-weight: 600 !important;
    }
    label, .stMarkdown p, span {
        color: #1e293b !important;
        font-weight: 600;
    }
    .stButton>button, .stFormSubmitButton>button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        width: 100%;
        padding: 8px 2px;
        font-size: 13px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Database Setup
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

# UI Top Header
st.markdown("""
    <div class="top-header">
        <p class="top-title">🏎️ MY SHIVSHAKTI AUTO PARTS & SERVICE</p>
        <p class="top-sub">📍 Main Road, Rantham, Chikhli, Malkapur (MH) &nbsp;|&nbsp; 📞 9158551896</p>
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

# TAB 1: BILLING
if st.session_state.menu_tab == "🛒 Billing":
    st.subheader("📝 New Customer Estimate & Billing")
    
    if "form_gen" not in st.session_state:
        st.session_state.form_gen = 0

    no_bill_mode = st.checkbox("⚡ Quick Direct Sale (बिना कस्टमर डिटेल के सीधा बिल)", value=False, key=f"nobill_{st.session_state.form_gen}")

    if not no_bill_mode:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            c_name = st.text_input("Customer Name", value="", placeholder="कस्टमर का नाम...", key=f"c_name_{st.session_state.form_gen}")
            c_mobile = st.text_input("Customer Mobile Number", value="", placeholder="मोबाइल नंबर...", key=f"c_mobile_{st.session_state.form_gen}")
        with col_c2:
            v_number = st.text_input("Vehicle Number", value="", placeholder="गाड़ी नंबर (MH19...)", key=f"v_num_{st.session_state.form_gen}").upper()
            v_model = st.text_input("Vehicle Model", value="", placeholder="गाड़ी मॉडल (Splendor...)", key=f"v_model_{st.session_state.form_gen}")
    else:
        c_name, c_mobile, v_number, v_model = "Counter Cash Customer", "", "NA", "Counter Sale"

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
            inventory_dict[item_name] = {"mrp": float(row['mrp']), "selling_price": float(row['selling_price']), "stock": int(row['stock'])}

    def update_item_fields():
        selected = st.session_state[f"sel_item_{st.session_state.form_gen}"]
        if selected != "-- Custom Item (मैन्युअल लिखें) --" and selected in inventory_dict:
            st.session_state[f"p_name_{st.session_state.form_gen}"] = selected
            st.session_state[f"p_mrp_{st.session_state.form_gen}"] = inventory_dict[selected]["mrp"]
            st.session_state[f"p_sell_{st.session_state.form_gen}"] = inventory_dict[selected]["selling_price"]

    st.selectbox("Select Part from Inventory", item_choices, key=f"sel_item_{st.session_state.form_gen}", on_change=update_item_fields)

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
            st.session_state.cart.append({
                "name": p_name_final, "mrp": final_mrp, "price": item_selling_input,
                "qty": qty_input, "total": item_selling_input * qty_input, "total_mrp": final_mrp * qty_input
            })
            st.rerun()

    if st.session_state.cart:
        st.markdown("---")
        st.markdown("### 📋 Current Bill Cart")
        parts_total_sum = sum(i['total'] for i in st.session_state.cart)
        total_mrp_sum = sum(i['total_mrp'] for i in st.session_state.cart)
        
        for idx, item in enumerate(st.session_state.cart):
            col_i1, col_i2, col_i3 = st.columns([3, 2, 1])
            with col_i1: st.write(f"• {item['name']} (x{item['qty']}) | MRP: ₹{item['mrp']} | Sell: ₹{item['price']}")
            with col_i2: st.write(f"₹{item['total']:.2f}")
            with col_i3:
                if st.button("❌", key=f"del_cart_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()

        total_savings = max(0.0, total_mrp_sum - parts_total_sum)
        
        if "labour_list" not in st.session_state:
            st.session_state.labour_list = []
            
        st.markdown("---")
        st.markdown("### 👨‍🔧 Add Labour & Services")
        col_l1, col_l2, col_l3 = st.columns([3, 2, 1])
        with col_l1: l_desc_input = st.text_input("Service Name", key=f"l_desc_{st.session_state.form_gen}")
        with col_l2: l_cost_input = st.number_input("Labour Cost (₹)", min_value=0.0, key=f"l_cost_{st.session_state.form_gen}")
        with col_l3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add Labour"):
                if l_desc_input and l_cost_input > 0:
                    st.session_state.labour_list.append({"desc": l_desc_input, "cost": l_cost_input})
                    st.rerun()

        total_labour_cost = sum(l['cost'] for l in st.session_state.labour_list)
        total_bill = parts_total_sum + total_labour_cost
        
        st.markdown(f"### 💥 Final Bill Amount: ₹{total_bill:.2f} (Savings: ₹{total_savings:.2f})")
        
        pay_mode = st.selectbox("Payment Mode", ["Cash", "Online/UPI", "Udhar (Credit)"], key=f"pm_{st.session_state.form_gen}")
        amount_paid = st.number_input("Amount Paid (₹)", min_value=0.0, max_value=float(total_bill), value=float(total_bill), key=f"ap_{st.session_state.form_gen}")
        balance_due = max(0.0, total_bill - amount_paid)

        if st.button("💾 Save Bill"):
            current_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
            items_str = ", ".join([f"{i['name']} (x{i['qty']})" for i in st.session_state.cart])
            labour_str = ", ".join([f"{l['desc']} (₹{l['cost']})" for l in st.session_state.labour_list])
            
            cursor.execute('''
                INSERT INTO sales (customer_name, customer_mobile, vehicle_number, vehicle_model, items_summary, parts_total, total_mrp_sum, total_savings, labour_desc, labour_cost, total_bill, amount_paid, balance_due, payment_mode, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (c_name, c_mobile, v_number, v_model, items_str, parts_total_sum, total_mrp_sum, total_savings, labour_str, total_labour_cost, total_bill, amount_paid, balance_due, pay_mode, current_date))
            
            for item in st.session_state.cart:
                cursor.execute("UPDATE parts SET stock = stock - ? WHERE name = ?", (item['qty'], item['name']))
            conn.commit()
            st.success("✅ Bill Saved Successfully!")

# TAB 2: INVENTORY STOCK (WITH EDIT & DELETE)
elif st.session_state.menu_tab == "📦 Stock":
    st.subheader("📦 Inventory Stock Management")
    
    with st.expander("➕ Add New Spare Part", expanded=False):
        with st.form("add_stock_form", clear_on_submit=True):
            p_name = st.text_input("Part Name")
            p_mrp = st.number_input("MRP (₹)", min_value=0.0, step=10.0)
            p_price = st.number_input("Selling Price (₹)", min_value=0.0, step=10.0)
            p_stock = st.number_input("Stock Quantity", min_value=0, value=10)
            if st.form_submit_button("Save Part"):
                if p_name and p_price > 0:
                    cursor.execute("INSERT INTO parts (name, mrp, selling_price, stock) VALUES (?, ?, ?, ?)", (p_name, p_mrp, p_price, p_stock))
                    conn.commit()
                    st.success("Part Added!")
                    st.rerun()

    stock_df = pd.read_sql("SELECT * FROM parts", conn)
    
    if not stock_df.empty:
        st.markdown("---")
        st.markdown("### ✏️ Edit or Delete Existing Item")
        part_options = {f"{row['name']} (ID: {row['id']})": row['id'] for _, row in stock_df.iterrows()}
        selected_part_str = st.selectbox("Select Part to Edit/Delete", list(part_options.keys()))
        selected_id = part_options[selected_part_str]
        selected_part_data = stock_df[stock_df['id'] == selected_id].iloc[0]
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown("#### ✏️ Update Item")
            edit_name = st.text_input("Edit Name", value=selected_part_data['name'])
            edit_mrp = st.number_input("Edit MRP (₹)", min_value=0.0, value=float(selected_part_data['mrp']))
            edit_sell = st.number_input("Edit Selling Price (₹)", min_value=0.0, value=float(selected_part_data['selling_price']))
            edit_stock = st.number_input("Edit Stock Qty", min_value=0, value=int(selected_part_data['stock']))
            
            if st.button("💾 Update Details"):
                cursor.execute("UPDATE parts SET name = ?, mrp = ?, selling_price = ?, stock = ? WHERE id = ?", (edit_name, edit_mrp, edit_sell, edit_stock, selected_id))
                conn.commit()
                st.success("Updated!")
                st.rerun()

        with col_e2:
            st.markdown("#### 🗑️ Remove Item")
            st.warning(f"Delete '{selected_part_data['name']}'?")
            if st.button("❌ Permanently Delete Item"):
                cursor.execute("DELETE FROM parts WHERE id = ?", (selected_id,))
                conn.commit()
                st.success("Deleted!")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Current Stock List")
    st.dataframe(stock_df, use_container_width=True)

# TAB 3: UDHAR
elif st.session_state.menu_tab == "📖 Udhar":
    st.subheader("📖 Udhar Register")
    udhar_df = pd.read_sql("SELECT * FROM sales WHERE balance_due > 0 ORDER BY id DESC", conn)
    if not udhar_df.empty:
        for _, row in udhar_df.iterrows():
            with st.expander(f"👤 {row['customer_name']} | 🚗 {row['vehicle_number']} | Due: ₹{row['balance_due']:.2f}"):
                recv_amt = st.number_input("Payment Received (₹)", min_value=0.0, max_value=float(row['balance_due']), value=float(row['balance_due']), key=f"ud_{row['id']}")
                if st.button("Update Payment", key=f"ubtn_{row['id']}"):
                    new_paid = row['amount_paid'] + recv_amt
                    new_due = max(0.0, row['balance_due'] - recv_amt)
                    cursor.execute("UPDATE sales SET amount_paid = ?, balance_due = ? WHERE id = ?", (new_paid, new_due, row['id']))
                    conn.commit()
                    st.rerun()
    else:
        st.success("कोई उधारी नहीं है!")

# TAB 4: RECORDS
elif st.session_state.menu_tab == "📊 Records":
    st.subheader("📊 Sales History")
    sales_df = pd.read_sql("SELECT * FROM sales ORDER BY id DESC", conn)
    st.dataframe(sales_df, use_container_width=True)
        
