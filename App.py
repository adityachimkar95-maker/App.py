import base64
from datetime import datetime
import sqlite3
import urllib.parse
import pandas as pd
import streamlit as st

# 🎨 पेज कॉन्फ़िगरेशन (मोबाइल और डेस्कटॉप के लिए ऑप्टिमाइज़्ड)
st.set_page_config(
    page_title="My Shivshakti Auto Parts & Service",
    layout="wide",
    page_icon="🏍️",
)

# 🌟 स्टाइलिश, स्वच्छ और टच-फ्रेंडली CSS
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)


# --------------------------------------------------------
# डेटाबेस सेटअप (Database Setup)
# --------------------------------------------------------
@st.cache_resource
def get_db_connection():
  conn = sqlite3.connect("autoparts_shop_v13.db", check_same_thread=False)
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            mrp REAL,
            selling_price REAL,
            stock INTEGER
        )
    """)

  cursor.execute("""
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
    """)
  conn.commit()
  return conn


conn = get_db_connection()
cursor = conn.cursor()

# --------------------------------------------------------
# सेशन स्टेट इनिशियलाइजेशन (Session State)
# --------------------------------------------------------
if "menu_tab" not in st.session_state:
  st.session_state.menu_tab = "🛒 बिलिंग (Billing)"
if "form_gen" not in st.session_state:
  st.session_state.form_gen = 0
if "cart" not in st.session_state:
  st.session_state.cart = []
if "labour_list" not in st.session_state:
  st.session_state.labour_list = []
if "extra_list" not in st.session_state:
  st.session_state.extra_list = []

# --------------------------------------------------------
# हेडर और नेविगेशन बटन (Header & Menu)
# --------------------------------------------------------
st.markdown(
    """
    <div class="top-header">
        <p class="top-title">🏍️ माय शिवशक्ति ऑटो पार्ट्स एंड सर्विस सेंटर</p>
        <p class="top-sub">📍 मेन रोड, रणथम, चिखली, मलकापुर (MH) &nbsp;|&nbsp;
        मालिक - श्री आदित्य युवराज चिमकर 📞 9158551896</p>
    </div>
""",
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
with m1:
  if st.button("🛒 बिलिंग (Billing)", key="btn_bill"):
    st.session_state.menu_tab = "🛒 बिलिंग (Billing)"
    st.rerun()
with m2:
  if st.button("📦 स्टॉक (Stock)", key="btn_stock"):
    st.session_state.menu_tab = "📦 स्टॉक (Stock)"
    st.rerun()
with m3:
  if st.button("📖 उधार खाता (Udhar)", key="btn_udhar"):
    st.session_state.menu_tab = "📖 उधार खाता (Udhar)"
    st.rerun()
with m4:
  if st.button("📊 रिकॉर्ड्स (Records)", key="btn_records"):
    st.session_state.menu_tab = "📊 रिकॉर्ड्स (Records)"
    st.rerun()

st.markdown("---")

# --------------------------------------------------------
# टैब 1: बिलिंग एवं एस्टिमेट (Billing & Estimate)
# --------------------------------------------------------
if st.session_state.menu_tab == "🛒 बिलिंग (Billing)":
  st.subheader("📝 नया कस्टमर बिल और एस्टिमेट")

  no_bill_mode = st.checkbox(
      "⚡ क्विक डायरेक्ट सेल (बिना कस्टमर डिटेल के सीधा बिल)",
      value=False,
      key=f"nobill_{st.session_state.form_gen}",
  )

  if not no_bill_mode:
    col_c1, col_c2 = st.columns(2)
    with col_c1:
      c_name = st.text_input(
          "कस्टमर का नाम",
          value="",
          placeholder="कस्टमर का नाम लिखें...",
          key=f"c_name_{st.session_state.form_gen}",
      )
      c_mobile = st.text_input(
          "मोबाइल नंबर",
          value="",
          placeholder="१० अंकों का नंबर लिखें...",
          key=f"c_mobile_{st.session_state.form_gen}",
      )
    with col_c2:
      v_number = st.text_input(
          "गाड़ी नंबर",
          value="",
          placeholder="उदा. MH28AB1234",
          key=f"v_num_{st.session_state.form_gen}",
      ).upper()
      v_model = st.text_input(
          "गाड़ी का मॉडल",
          value="",
          placeholder="उदा. Splendor, Shine...",
          key=f"v_model_{st.session_state.form_gen}",
      )
  else:
    c_name, c_mobile, v_number, v_model = (
        "काउंटर कैश कस्टमर",
        "",
        "NA",
        "काउंटर सेल",
    )
    st.info("⚡ क्विक मोड चालू है: कस्टमर डिटेल्स की आवश्यकता नहीं है।")

  st.markdown("---")
  st.markdown("### ➕ स्पेयर पार्ट्स जोड़ें (Add Parts)")

  inv_df = pd.read_sql("SELECT * FROM parts", conn)
  inventory_dict = {}
  item_choices = ["-- कस्टम आइटम (मैन्युअल लिखें) --"]

  if not inv_df.empty:
    for _, row in inv_df.iterrows():
      item_name = row["name"]
      item_choices.append(item_name)
      inventory_dict[item_name] = {
          "mrp": float(row["mrp"]),
          "selling_price": float(row["selling_price"]),
          "stock": int(row["stock"]),
      }

  def update_item_fields():
    selected = st.session_state[f"sel_item_{st.session_state.form_gen}"]
    if selected in inventory_dict:
      st.session_state[f"p_name_{st.session_state.form_gen}"] = selected
      st.session_state[f"p_mrp_{st.session_state.form_gen}"] = inventory_dict[
          selected
      ]["mrp"]
      st.session_state[f"p_sell_{st.session_state.form_gen}"] = inventory_dict[
          selected
      ]["selling_price"]
    else:
      st.session_state[f"p_name_{st.session_state.form_gen}"] = ""
      st.session_state[f"p_mrp_{st.session_state.form_gen}"] = 0.0
      st.session_state[f"p_sell_{st.session_state.form_gen}"] = 0.0

  st.selectbox(
      "स्टॉक से पार्ट चुनें",
      item_choices,
      key=f"sel_item_{st.session_state.form_gen}",
      on_change=update_item_fields,
  )

  if f"p_name_{st.session_state.form_gen}" not in st.session_state:
    st.session_state[f"p_name_{st.session_state.form_gen}"] = ""
  if f"p_mrp_{st.session_state.form_gen}" not in st.session_state:
    st.session_state[f"p_mrp_{st.session_state.form_gen}"] = 0.0
  if f"p_sell_{st.session_state.form_gen}" not in st.session_state:
    st.session_state[f"p_sell_{st.session_state.form_gen}"] = 0.0

  col_a, col_b, col_c, col_d = st.columns(4)
  with col_a:
    p_name_final = st.text_input(
        "पार्ट का नाम", key=f"p_name_{st.session_state.form_gen}"
    )
  with col_b:
    item_mrp_input = st.number_input(
        "MRP (₹)",
        min_value=0.0,
        step=10.0,
        key=f"p_mrp_{st.session_state.form_gen}",
    )
  with col_c:
    item_selling_input = st.number_input(
        "बेचने का भाव / Selling Price (₹)",
        min_value=0.0,
        step=10.0,
        key=f"p_sell_{st.session_state.form_gen}",
    )
  with col_d:
    qty_input = st.number_input(
        "मात्रा (Qty)",
        min_value=1,
        value=1,
        key=f"p_qty_{st.session_state.form_gen}",
    )

  if st.button("➕ बिल कार्ट में जोड़ें"):
    if p_name_final and item_selling_input > 0:
      final_mrp = item_mrp_input if item_mrp_input > 0 else item_selling_input
      st.session_state.cart.append({
          "name": p_name_final,
          "mrp": final_mrp,
          "price": item_selling_input,
          "qty": qty_input,
          "total": item_selling_input * qty_input,
          "total_mrp": final_mrp * qty_input,
      })
      st.success(f"{p_name_final} बिल में जोड़ दिया गया है!")
      st.rerun()
    else:
      st.warning("⚠️ कृपया सही पार्ट का नाम और सेलिंग प्राइस दर्ज करें!")

  parts_total_sum, total_mrp_sum = 0.0, 0.0
  if st.session_state.cart:
    st.markdown("---")
    st.markdown("### 📋 वर्तमान सामान सूची (Current Cart)")
    for idx, item in enumerate(st.session_state.cart):
      parts_total_sum += item["total"]
      total_mrp_sum += item["total_mrp"]

      col_i1, col_i2, col_i3 = st.columns([4, 2, 1])
      with col_i1:
        st.markdown(
            f"**{idx+1}. {item['name']}** (x{item['qty']})<br>MRP: ₹{item['mrp']}"
            f" | रेट: ₹{item['price']}",
            unsafe_allow_html=True,
        )
      with col_i2:
        st.markdown(
            f"<br><b>₹{item['total']:.2f}</b>", unsafe_allow_html=True
        )
      with col_i3:
        if st.button("🗑️ हटाएं", key=f"del_cart_{idx}"):
          st.session_state.cart.pop(idx)
          st.rerun()

    total_savings = max(0.0, total_mrp_sum - parts_total_sum)
    st.markdown(f"""
        <div style="background: #dcfce7; border: 1px solid #22c55e; padding: 12px; border-radius: 8px; margin: 12px 0;">
            <span style="color: #166534; font-size: 16px; font-weight: bold;">🎉 कस्टमर की कुल बचत (MRP डिस्काउंट): ₹{total_savings:.2f}</span>
        </div>
    """, unsafe_allow_html=True)
  else:
    total_savings = 0.0

  st.markdown("---")
  st.markdown("### 👨‍🔧 लेबर सर्विस चार्ज (Labour Charge)")
  col_l1, col_l2, col_l3, col_l4 = st.columns([3, 2, 1, 1])
  with col_l1:
    l_desc_input = st.text_input(
        "काम का विवरण",
        placeholder="उदा. फुल सर्विसिंग",
        key=f"l_desc_input_{st.session_state.form_gen}",
    )
  with col_l2:
    l_cost_input = st.number_input(
        "रेट (₹)",
        min_value=0.0,
        step=10.0,
        key=f"l_cost_input_{st.session_state.form_gen}",
    )
  with col_l3:
    l_qty_input = st.number_input(
        "मात्रा",
        min_value=1,
        value=1,
        key=f"l_qty_input_{st.session_state.form_gen}",
    )
  with col_l4:
    if st.button("➕ लेबर जोड़ें"):
      if l_desc_input and l_cost_input > 0:
        st.session_state.labour_list.append({
            "desc": l_desc_input,
            "cost": l_cost_input,
            "qty": l_qty_input,
            "total": l_cost_input * l_qty_input,
        })
        st.rerun()

  total_labour_cost = sum(
      lab["total"] for lab in st.session_state.labour_list
  )
  for l_idx, lab in enumerate(st.session_state.labour_list):
    cl1, cl2 = st.columns([5, 1])
    with cl1:
      st.write(
          f"👉 **{lab['desc']}** (Qty: {lab['qty']}) - ₹{lab['cost']} = कुल"
          f" ₹{lab['total']:.2f}"
      )
    with cl2:
      if st.button("🗑️", key=f"del_lab_{l_idx}"):
        st.session_state.labour_list.pop(l_idx)
        st.rerun()

  st.markdown("---")
  st.markdown("### 🛠️ अन्य काम/चार्ज (Extra Charges)")
  col_e1, col_e2, col_e3, col_e4 = st.columns([3, 2, 1, 1])
  with col_e1:
    e_desc_input = st.text_input(
        "एक्स्ट्रा काम का नाम",
        placeholder="उदा. वेल्डिंग चार्ज",
        key=f"e_desc_input_{st.session_state.form_gen}",
    )
  with col_e2:
    e_cost_input = st.number_input(
        "रेट (₹)",
        min_value=0.0,
        step=10.0,
        key=f"e_cost_input_{st.session_state.form_gen}",
    )
  with col_e3:
    e_qty_input = st.number_input(
        "मात्रा",
        min_value=1,
        value=1,
        key=f"e_qty_input_{st.session_state.form_gen}",
    )
  with col_e4:
    if st.button("➕ काम जोड़ें"):
      if e_desc_input and e_cost_input > 0:
        st.session_state.extra_list.append({
            "desc": e_desc_input,
            "cost": e_cost_input,
            "qty": e_qty_input,
            "total": e_cost_input * e_qty_input,
        })
        st.rerun()

  total_extra_cost = sum(ext["total"] for ext in st.session_state.extra_list)
  for e_idx, ext in enumerate(st.session_state.extra_list):
    cel1, cel2 = st.columns([5, 1])
    with cel1:
      st.write(
          f"👉 **{ext['desc']}** (Qty: {ext['qty']}) - ₹{ext['cost']} = कुल"
          f" ₹{ext['total']:.2f}"
      )
    with cel2:
      if st.button("🗑️", key=f"del_ext_{e_idx}"):
        st.session_state.extra_list.pop(e_idx)
        st.rerun()

  # कुल बिल गणना
  total_bill = parts_total_sum + total_labour_cost + total_extra_cost
  st.markdown(f"""
        <div style="background: #fef3c7; border: 2px solid #f59e0b; padding: 18px; border-radius: 12px; margin: 15px 0; text-align: center;">
            <h2 style="color: #b45309; margin: 0; font-size: 24px;">💥 कुल बिल राशि: ₹{total_bill:.2f}</h2>
        </div>
    """, unsafe_allow_html=True)

  pay_mode = st.selectbox(
      "भुगतान का प्रकार (Payment Mode)",
      ["कैश (Cash)", "ऑनलाइन/UPI (Online)", "उधार (Credit)"],
      key=f"pay_mode_{st.session_state.form_gen}",
  )
  amount_paid = st.number_input(
      "प्राप्त राशि / जमा राशि (₹)",
      min_value=0.0,
      max_value=float(total_bill),
      value=float(total_bill),
      key=f"amt_paid_{st.session_state.form_gen}",
  )
  balance_due = max(0.0, total_bill - amount_paid)

  if st.button("💾 बिल सेव करें और पर्ची जनरेट करें"):
    if not no_bill_mode and (not c_name or not v_number):
      st.warning("⚠️ कृपया कस्टमर का नाम और गाड़ी नंबर दर्ज करें।")
    else:
      current_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
      items_desc_list = [
          f"{item['name']} (x{item['qty']})" for item in st.session_state.cart
      ]
      labour_final_desc_str = ", ".join(
          [f"{lab['desc']} (x{lab['qty']})" for lab in st.session_state.labour_list]
      )
      extra_final_desc_str = ", ".join(
          [f"{ext['desc']} (x{ext['qty']})" for ext in st.session_state.extra_list]
      )

      cursor.execute(
          """
                INSERT INTO sales (customer_name, customer_mobile, vehicle_number, vehicle_model, items_summary, parts_total, total_mrp_sum, total_savings, labour_desc, labour_cost, extra_desc, extra_cost, total_bill, amount_paid, balance_due, payment_mode, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
          (
              c_name,
              c_mobile,
              v_number,
              v_model,
              ", ".join(items_desc_list),
              parts_total_sum,
              total_mrp_sum,
              total_savings,
              labour_final_desc_str,
              total_labour_cost,
              extra_final_desc_str,
              total_extra_cost,
              total_bill,
              amount_paid,
              balance_due,
              pay_mode,
              current_date,
          ),
      )

      # स्टॉक में से सामान घटाना
      for item in st.session_state.cart:
        cursor.execute(
            "UPDATE parts SET stock = stock - ? WHERE name = ?",
            (item["qty"], item["name"]),
        )

      conn.commit()

      # डेटा रीसेट करना (Clear Form for Next Customer)
      st.session_state.cart = []
      st.session_state.labour_list = []
      st.session_state.extra_list = []
      st.session_state.form_gen += 1
      st.success("✅ बिल सफलतापूर्वक सेव हो गया!")
      st.rerun()

  # 📲 व्हाट्सएप और डाउनलोड सेक्शन
  formatted_items = "\n".join([
      f"{idx+1}. {i['name']} (x{i['qty']}) = ₹{i['total']:.2f}"
      for idx, i in enumerate(st.session_state.cart)
  ])
  slip_text = (
      "🏍️ *माय शिवशक्ति ऑटो पार्ट्स*\n"
      f"कस्टमर: {c_name}\nगाड़ी नंबर: {v_number}\nकुल बिल: ₹{total_bill:.2f}\nबाकी"
      f" राशि: ₹{balance_due:.2f}\n\nसामान की सूची:\n{formatted_items}\n\nधन्यवाद!"
  )

  st.markdown("---")
  st.markdown("### 📤 बिल शेयर करें या डाउनलोड करें")
  col_s1, col_s2 = st.columns(2)
  with col_s1:
    clean_mobile = (
        "91" + c_mobile.replace("+", "").replace(" ", "")
        if len(c_mobile) == 10
        else c_mobile
    )
    wa_link = (
        f"https://wa.me/{clean_mobile}?text={urllib.parse.quote(slip_text)}"
    )
    st.link_button("📲 व्हाट्सएप पर भेजें (WhatsApp)", wa_link)
  with col_s2:
    print_html = f"""
        <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2>माय शिवशक्ति ऑटो पार्ट्स एंड सर्विस सेंटर</h2>
            <p><b>कस्टमर:</b> {c_name} | <b>मोबाइल:</b> {c_mobile}</p>
            <p><b>गाड़ी नंबर:</b> {v_number} | <b>मॉडल:</b> {v_model}</p>
            <hr>
            <h3>कुल बिल: ₹{total_bill:.2f}</h3>
            <p><b>जमा:</b> ₹{amount_paid:.2f} | <b>बाकी (उधार):</b> ₹{balance_due:.2f}</p>
        </body>
        </html>
    """
    b64 = base64.b64encode(print_html.encode()).decode()
    st.markdown(
        f'<a href="data:text/html;base64,{b64}" download="Bill_{v_number}.html" target="_blank"><button style="width:100%; padding:10px; border-radius:10px; background:#2563eb; color:white; border:none; font-weight:bold;">🖨️ बिल प्रिंट / डाउनलोड करें</button></a>',
        unsafe_allow_html=True,
    )

# --------------------------------------------------------
# टैब 2: स्टॉक मैनेजमेंट (Stock Management)
# --------------------------------------------------------
elif st.session_state.menu_tab == "📦 स्टॉक (Stock)":
  st.subheader("📦 दुकान का स्टॉक मैनेजमेंट (Inventory)")

  with st.form("add_parts_form", clear_on_submit=True):
    st.markdown("#### ➕ नया स्पेयर पार्ट स्टॉक में जोड़ें")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
      new_pname = st.text_input("पार्ट का नाम")
    with col_s2:
      new_mrp = st.number_input("MRP (₹)", min_value=0.0, step=10.0)
    with col_s3:
      new_sell = st.number_input("बेचने का रेट (₹)", min_value=0.0, step=10.0)
    with col_s4:
      new_stock = st.number_input("शुरुआती मात्रा (Stock Qty)", min_value=0, step=1)

    if st.form_submit_button("➕ स्टॉक में जोड़ें"):
      if new_pname and new_sell > 0:
        try:
          cursor.execute(
              "INSERT INTO parts (name, mrp, selling_price, stock) VALUES"
              " (?, ?, ?, ?)",
              (new_pname, new_mrp, new_sell, new_stock),
          )
          conn.commit()
          st.success(f"{new_pname} सफलतापूर्वक स्टॉक में जोड़ दिया गया!")
          st.rerun()
        except sqlite3.IntegrityError:
          st.error(
              "यह पार्ट पहले से मौजूद है! नाम बदलें या मौजूदा आइटम अपडेट करें।"
          )
      else:
        st.error("कृपया पार्ट का नाम और सही कीमत दर्ज करें।")

  st.markdown("---")
  st.markdown("#### 📊 वर्तमान उपलब्ध स्टॉक")
  inv_data = pd.read_sql("SELECT * FROM parts", conn)
  if not inv_data.empty:
    st.dataframe(inv_data, use_contai
