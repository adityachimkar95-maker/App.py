import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse
import base64

# 🎨 Page Configuration
st.set_page_config(
    page_title="My Shivshakti Auto Parts & Service",
    layout="wide",
    page_icon="🏎️"
)

# --------------------------------------------------------
# SUPABASE CONNECTION SETUP
# --------------------------------------------------------
supabase = None
try:
    from supabase import create_client
    if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception:
    pass

# 🌟 Clean & Mobile CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Inter', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    .top-header {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        border: 2px solid #cbd5e1; border-bottom: 4px solid #f59e0b;
        padding: 16px 10px; margin-bottom: 15px; text-align: center; border-radius: 12px;
    }
    .top-title { color: #d97706; font-size: 20px; font-weight: 900; margin: 0; }
    .top-sub { color: #334155; font-size: 12px; margin-top: 5px; font-weight: 700; }
    .stTextInput input, .stNumberInput input {
        background-color: #ffffff !important; color: #0f172a !important;
        border: 1.5px solid #94a3b8 !important; border-radius: 8px !important;
    }
    label, .stMarkdown p, span { color: #1e293b !important; font-weight: 600; }
    .stButton>button, .stFormSubmitButton>button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #ffffff !important; border-radius: 10px !important; font-weight: 800 !important;
        border: none !important; width: 100%; padding: 8px 2px;
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
        name TEXT, mrp REAL, selling_price REAL, stock INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, customer_mobile TEXT,
        vehicle_number TEXT, vehicle_model TEXT, items_summary TEXT, parts_total REAL,
        total_mrp_sum REAL, total_savings REAL, labour_desc TEXT, labour_cost REAL,
        total_bill REAL, amount_paid REAL, balance_due REAL, payment_mode TEXT, date TEXT
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
    st.markdown("### ➕ Add Items (MRP & Selling Price)")
    
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

    st.selectbox("Select Part from Inventory", item_choices, key=f"sel_item_{st.session_state.form_gen}", on_change=update_item_fields)

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
            st.session_state.cart.append({
                "name": p_name_final, "mrp": final_mrp, "price": item_selling_input,
                "qty": qty_input, "total": item_selling_input * qty_input, "total_mrp": final_mrp * qty_input
            })
            st.success(f"Added {p_name_final} to cart!")
            st.rerun()
        else:
            st.warning("⚠️ कृपया सही पार्ट का नाम और सेलिंग प्राइस दर्ज करें!")

    if st.session_state.cart:
        st.markdown("---")
        st.markdown("### 📋 Current Bill Cart")
        parts_total_sum, total_mrp_sum = 0.0, 0.0
        for idx, item in enumerate(st.session_state.cart):
            parts_total_sum += item['total']
            total_mrp_sum += item['total_mrp']
            col_i1, col_i2, col_i3 = st.columns([3, 2, 1])
            with col_i1:
                st.write(f"• {item['name']} (Qty: {item['qty']}) | MRP: ₹{item['mrp']} | Sell: ₹{item['price']}")
            with col_i2:
                st.write(f"₹{item['total']:.2f}")
            with col_i3:
                if st.button("❌", key=f"del_cart_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                    
        total_savings = max(0.0, total_mrp_sum - parts_total_sum)
        st.markdown(f"**🎉 Savings: ₹{total_savings:.2f}**")
        
        if "labour_list" not in st.session_state:
            st.session_state.labour_list = []
            
        col_l1, col_l2, col_l3 = st.columns([3, 2, 1])
        with col_l1:
            l_desc_input = st.text_input("Service / Labour Name", key=f"l_desc_input_{st.session_state.form_gen}")
        with col_l2:
            l_cost_input = st.number_input("Labour Cost (₹)", min_value=0.0, step=10.0, key=f"l_cost_input_{st.session_state.form_gen}")
        with col_l3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add Labour"):
                if l_desc_input and l_cost_input > 0:
                    st.session_state.labour_list.append({"desc": l_desc_input, "cost": l_cost_input})
                    st.rerun()

        total_labour_cost = sum([lab['cost'] for lab in st.session_state.labour_list])
        total_bill = parts_total_sum + total_labour_cost
        
        st.markdown(f"### 💥 Total: ₹{total_bill:.2f}")
        
        pay_mode = st.selectbox("Payment Mode", ["Cash", "Online/UPI", "Udhar (Credit)"], key=f"pay_mode_{st.session_state.form_gen}")
        amount_paid = st.number_input("Amount Paid (₹)", min_value=0.0, value=float(total_bill), key=f"amt_paid_{st.session_state.form_gen}")
        balance_due = max(0.0, total_bill - amount_paid)
        
        if st.button("💾 Save & Generate Bill"):
            current_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
            items_desc = ", ".join([f"{i['name']} (x{i['qty']})" for i in st.session_state.cart])
            labour_desc = ", ".join([f"{l['desc']} (₹{l['cost']})" for l in st.session_state.labour_list])
            
            cursor.execute('''
                INSERT INTO sales (customer_name, customer_mobile, vehicle_number, vehicle_model, items_summary, parts_total, total_mrp_sum, total_savings, labour_desc, labour_cost, total_bill, amount_paid, balance_due, payment_mode, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (c_name, c_mobile, v_number, v_model, items_desc, parts_total_sum, total_mrp_sum, total_savings, labour_desc, total_labour_cost, total_bill, amount_paid, balance_due, pay_mode, current_date))
            
            sale_id = cursor.lastrowid
            conn.commit()

            if supabase:
                try:
                    supabase.table("adityachimkar95-maker's Org").insert({
                        "title": f"Bill #{sale_id}: {c_name} ({v_number})",
                        "original_url": f"Total: ₹{total_bill} | Paid: ₹{amount_paid}"
                    }).execute()
                except Exception:
                    pass

            st.success(f"✅ Bill Saved #{sale_id}")

        if st.button("🔄 New Bill"):
            st.session_state.cart = []
            st.session_state.labour_list = []
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

                if supabase:
                    try:
                        supabase.table("adityachimkar95-maker's Org").insert({
                            "title": p_name,
                            "original_url": f"MRP: ₹{p_mrp} | Price: ₹{p_price} | Stock: {p_stock}"
                        }).execute()
                    except Exception:
                        pass

                st.success("✅ पार्ट स्टॉक में जोड़ दिया गया!")
                st.rerun()
            else:
                st.warning("कृपया नाम और सेलिंग प्राइस दर्ज करें।")
                
    stock_df = pd.read_sql("SELECT * FROM parts", conn)
    if not stock_df.empty:
        st.dataframe(stock_df, use_container_width=True)

# --------------------------------------------------------
# TAB 3: UDHAR KHATA
# --------------------------------------------------------
elif st.session_state.menu_tab == "📖 Udhar":
    st.subheader("📖 Udhar Khata")
    udhar_df = pd.read_sql("SELECT * FROM sales WHERE balance_due > 0", conn)
    if not udhar_df.empty:
        st.dataframe(udhar_df, use_container_width=True)
    else:
        st.success("🎉 कोई उधारी नहीं है!")

# --------------------------------------------------------
# TAB 4: RECORDS
# --------------------------------------------------------
elif st.session_state.menu_tab == "📊 Records":
    st.subheader("📊 Sales History")
    sales_df = pd.read_sql("SELECT * FROM sales ORDER BY id DESC", conn)
    if not sales_df.empty:
        st.dataframe(sales_df, use_container_width=True)
# --------------------------------------------------------
# LOAD PERSISTENT DATA FROM SUPABASE ON STARTUP
# --------------------------------------------------------
def load_data_from_supabase():
    if supabase:
        try:
            # Fetch saved records from Supabase
            res = supabase.table("adityachimkar95-maker's Org").select("*").execute()
            if res.data:
                for row in res.data:
                    # Sync titles back into local view if missing
                    pass
        except Exception as e:
            pass

load_data_from_supabase()
        
