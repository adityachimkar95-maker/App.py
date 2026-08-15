import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# Page Configuration
st.set_page_config(page_title="My Shivshakti Auto Parts & Service", layout="wide", page_icon="🏎️")

# Database Setup
conn = sqlite3.connect('shivshakti_garage_v3.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT, mrp REAL, selling_price REAL, stock INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS bills (
    bill_id TEXT, customer_name TEXT, phone TEXT, vehicle TEXT, mechanic_name TEXT, 
    payment_mode TEXT, parts_charges REAL, labor_charges REAL, total REAL, paid_amount REAL, balance_due REAL, date TEXT, items TEXT)''')
conn.commit()

# --- App UI ---
st.title("🏎️ MY SHIVSHAKTI AUTO PARTS & SERVICE")
st.caption("📍 Main Road, Rantham, Chikhli, Malkapur (MH) | 📞 9158551896")

tab1, tab2, tab3 = st.tabs(["📝 Billing", "📦 Inventory", "📊 Records"])

with tab1:
    st.subheader("New Service Bill")
    
    col1, col2 = st.columns(2)
    with col1:
        cust_name = st.text_input("Customer Name", placeholder="e.g. Aditya chimkar")
        phone = st.text_input("Phone Number (with 91)", value="91")
        mechanic = st.text_input("Mechanic Name")
    with col2:
        vehicle = st.text_input("Vehicle Number", placeholder="e.g. MH19CH9695")
        pay_mode = st.selectbox("Payment Mode", ["Cash", "Online/UPI", "Udhar (Credit)"])

    if "cart" not in st.session_state: 
        st.session_state.cart = []
    
    # Item/Service Addition Section
    st.markdown("---")
    st.markdown("### ➕ Add Parts or Labor/Work")
    
    inv = pd.read_sql("SELECT * FROM inventory", conn)
    item_options = ["-- Custom Item / Work --"] + inv['item_name'].tolist() if not inv.empty else ["-- Custom Item / Work --"]
    
    with st.form("add_item_form", clear_on_submit=True):
        selected_item = st.selectbox("Select Part from Inventory", item_options)
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            item_type = st.selectbox("Type", ["Parts", "Labor / Work"])
        with col_b:
            custom_name = st.text_input("Custom Name (e.g. Chine clining)")
        with col_c:
            custom_price = st.number_input("Charges / Price (₹)", min_value=0.0, step=10.0)
            
        qty = st.number_input("Quantity", min_value=1, value=1)
        add_btn = st.form_submit_button("Add to Bill")
        
        if add_btn:
            if selected_item != "-- Custom Item / Work --":
                row = inv[inv['item_name'] == selected_item].iloc[0]
                final_name = selected_item
                final_price = row['selling_price']
            else:
                final_name = custom_name
                final_price = custom_price
                
            if final_name:
                st.session_state.cart.append({
                    "name": final_name, 
                    "type": item_type, 
                    "price": final_price, 
                    "qty": qty
                })
                st.success(f"Added {final_name} successfully!")
                st.rerun()
            else:
                st.warning("Please provide a name or select an item.")

    # Display Current Cart / Bill Summary
    if st.session_state.cart:
        st.markdown("---")
        st.markdown("### 🧾 Current Bill Breakdown")
        
        df_cart = pd.DataFrame(st.session_state.cart)
        df_cart['subtotal'] = df_cart['price'] * df_cart['qty']
        
        for idx, row in df_cart.iterrows():
            col_x, col_y, col_z = st.columns([3, 2, 1])
            with col_x:
                st.write(f"**{row['name']}** ({row['type']}) x {row['qty']}")
            with col_y:
                st.write(f"₹{row['subtotal']:.2f}")
            with col_z:
                if st.button("❌", key=f"remove_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
        
        # Calculate parts vs labor charges
        parts_charges = df_cart[df_cart['type'] == 'Parts']['subtotal'].sum()
        labor_charges = df_cart[df_cart['type'] == 'Labor / Work']['subtotal'].sum()
        total_bill = parts_charges + labor_charges
        
        st.info(f"📦 Parts: ₹{parts_charges:.2f} | 👨‍🔧 Labor: ₹{labor_charges:.2f} | 💰 **Total: ₹{total_bill:.2f}**")
        
        paid_amount = st.number_input("Paid Amount (₹)", min_value=0.0, max_value=float(total_bill), value=float(total_bill), step=10.0)
        pending_udhar = total_bill - paid_amount
        
        if st.button("💾 Save Bill & Generate WhatsApp Message"):
            if not cust_name or not vehicle:
                st.warning("⚠️ Please enter Customer Name and Vehicle Number.")
            else:
                bill_id = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                # Fixed formatting variables (Fixed unmatched parenthesis error here)
                work_details_str = "\n".join([f"- {i['name']} (x{i['qty']})" for i in st.session_state.cart])
                items_db_str = ", ".join([f"{i['name']} (x{i['qty']})" for i in st.session_state.cart])
                
                c.execute("INSERT INTO bills VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          (bill_id, cust_name, phone, vehicle, mechanic, pay_mode, parts_charges, labor_charges, total_bill, paid_amount, pending_udhar, date_str, items_db_str))
                conn.commit()
                
                st.success("✅ Bill Saved Successfully in Records!")
                
                # Exact WhatsApp Template requested
                wa_msg = f"""🏎️ *MY SHIVSHAKTI AUTO PARTS & SERVICE*
📍 Main Road, Rantham, Chikhli, Malkapur (MH)
📞 9158551896
-----------------------------------
👤 *Customer:* {cust_name}
🚘 *Vehicle No:* {vehicle}
📅 *Date:* {date_str}
-----------------------------------
🔧 *Work Details:* 
{work_details_str}
-----------------------------------
📦 *Parts Charges:* ₹{parts_charges:.2f}
👨‍🔧 *Labor Charges:* ₹{labor_charges:.2f}
💰 *Total Bill:* ₹{total_bill:.2f}
✅ *Paid Amount:* ₹{paid_amount:.2f}
🔴 *Pending Udhar:* ₹{pending_udhar:.2f}
-----------------------------------
🙏 *धन्यवाद!*"""

                encoded_whatsapp_url = f"https://wa.me/{phone}?text={urllib.parse.quote(wa_msg)}"
                st.link_button("📲 Send WhatsApp Bill to Customer", encoded_whatsapp_url)
                
                if st.button("🔄 Clear & Start New Bill"):
                    st.session_state.cart = []
                    st.rerun()

with tab2:
    st.subheader("📦 Manage Inventory & Spares")
    with st.form("inv_form", clear_on_submit=True):
        i_name = st.text_input("Part/Item Name")
        i_mrp = st.number_input("MRP (₹)", min_value=0.0, step=10.0)
        i_price = st.number_input("Selling Price (₹)", min_value=0.0, step=10.0)
        i_stock = st.number_input("Stock Quantity", min_value=0, value=10)
        
        if st.form_submit_button("Save to Inventory"):
            if i_name:
                c.execute("INSERT INTO inventory (item_name, mrp, selling_price, stock) VALUES (?,?,?,?)", 
                          (i_name, i_mrp, i_price, i_stock))
                conn.commit()
                st.success(f"Added {i_name} to inventory!")
                st.rerun()
            else:
                st.warning("Please enter item name.")
                
    inv_df = pd.read_sql("SELECT * FROM inventory", conn)
    if not inv_df.empty:
        st.dataframe(inv_df, use_container_width=True)
    else:
        st.info("No spare parts added in inventory yet.")

with tab3:
    st.subheader("📊 Saved Bills & Ledger Records")
    bills_df = pd.read_sql("SELECT * FROM bills ORDER BY date DESC", conn)
    if not bills_df.empty:
        st.dataframe(bills_df, use_container_width=True)
    else:
        st.info("No bills recorded yet.")
