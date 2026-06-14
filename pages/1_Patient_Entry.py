import sys
import os
import streamlit as st
import sqlite3

# 1. Global Path Setup & Sidebar Load
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from sidebar_monitor import show_live_sidebar
    show_live_sidebar()
except Exception:
    pass

# --- Database Connection ---
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# Create Tables
c.execute("""CREATE TABLE IF NOT EXISTS billing_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    patient_name TEXT, 
    age INT, 
    phone TEXT, 
    selected_tests TEXT, 
    total_amount REAL, 
    discount REAL, 
    advance REAL, 
    due REAL, 
    date TEXT, 
    doctor_name TEXT,
    created_by TEXT)""")

# Safe alter to guarantee columns exist
try:
    c.execute("ALTER TABLE billing_records ADD COLUMN discount REAL")
    conn.commit()
except Exception:
    pass

try:
    c.execute("ALTER TABLE billing_records ADD COLUMN discount_amount REAL")
    conn.commit()
except Exception:
    pass

try:
    c.execute("ALTER TABLE billing_records ADD COLUMN created_by TEXT")
    conn.commit()
except Exception:
    pass

c.execute("""CREATE TABLE IF NOT EXISTS doctors_list (id INTEGER PRIMARY KEY AUTOINCREMENT, doc_name TEXT UNIQUE)""")
c.execute("""CREATE TABLE IF NOT EXISTS custom_tests_list (id INTEGER PRIMARY KEY AUTOINCREMENT, test_name TEXT UNIQUE)""")
c.execute("""CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT DEFAULT 'staff')""")
c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
conn.commit()

# --- 2. Secure Login System ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in or 'username' not in st.session_state:
    st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>🔑 Counter Login Panel</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        username_input = st.text_input("Username").strip()
        password_input = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login to Dashboard", use_container_width=True)
        
        if login_btn:
            if username_input and password_input:
                c.execute("SELECT password, role FROM users WHERE username = ?", (username_input,))
                user_data = c.fetchone()
                if user_data and user_data[0] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.session_state.role = user_data[1]
                    st.success(f"Welcome {username_input}! Loading system...")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password!")
            else:
                st.warning("Please enter both Username and Password.")
    st.stop()

# --- 3. Custom UI Styling ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stApp label { color: #8b949e !important; font-weight: 500 !important; font-size: 0.95rem !important; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    [data-testid="stSidebar"] * { color: #c9d1d9 !important; }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stMultiSelect div {
        background-color: #161b22 !important; color: #ffffff !important; border: 1px solid #30363d !important;
    }
    [data-testid="stMetricBlock"] { background-color: #161b22 !important; border: 1px solid #30363d !important; border-radius: 8px !important; padding: 10px !important; }
    [data-testid="stMetricValue"] { color: #238636 !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] { color: #8b949e !important; }
    .stButton button { background-color: #238636 !important; color: white !important; border-radius: 6px !important; padding: 0.5rem 1rem !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

current_user = st.session_state.get('username', 'Unknown')
st.markdown(f"<div style='text-align: right; color: #8b949e; font-weight: bold;'>👤 Current Operator: <span style='color: #58a6ff;'>{current_user}</span></div>", unsafe_allow_html=True)
st.markdown("<marquee style='color: #ff7b72; font-weight: bold;'>⚠️ Warning: Please double check all data before submitting the billing form.</marquee>", unsafe_allow_html=True)

# Fetch Lists
c.execute("SELECT doc_name FROM doctors_list")
db_doctors = [row[0] for row in c.fetchall() if row and row[0]]
doctor_options = db_doctors + ["Other"]

default_laboratory_tests = ["CBC", "ESR", "TC.DC", "Hgb", "Platelet Count", "MP", "BT/CT", "C/E Count", "Widal", "Aslo Titre"]
available_tests = list(default_laboratory_tests)

try:
    c.execute("SELECT test_name FROM custom_tests_list")
    db_tests = c.fetchall()
    for row in db_tests:
        if row and row[0] not in available_tests:
            available_tests.append(row[0])
except Exception:
    pass
available_tests.sort()

# --- 4. Form Layout ---
st.title("🏥 Rogmukti X-Ray & Digital Lab")
st.subheader("📋 Patient Entry Form")

col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("Patient Name *")
    phone = st.text_input("Mobile Number *")
with col2:
    age = st.number_input("Patient Age", min_value=1, max_value=120, value=25)
    selected_doctor_setup = st.selectbox("Referred By *", doctor_options)

if selected_doctor_setup == "Other":
    doctor_text = st.text_input("Enter New Doctor Name & Degree: *")
    if doctor_text:
        selected_doctor_setup = doctor_text.strip()

st.subheader("🔬 Test Selection & Pricing")
selected_tests = st.multiselect("Select Tests from List:", available_tests)

test_with_prices = []
total_fee = 0.0

if selected_tests:
    st.markdown("##### 💰 Enter Fee for Selected Tests:")
    for test in selected_tests:
        price_input = st.number_input(f"Fee for ({test}):", min_value=0.0, step=50.0, value=None, placeholder="Enter price...", key=f"p_{test}")
        price = price_input if price_input is not None else 0.0
        total_fee += price
        test_with_prices.append(f"{test}({price})")

st.markdown("##### ➕ Add Extra Test (Optional):")
col_c1, col_c2 = st.columns(2)
with col_c1:
    custom_name = st.text_input("Custom Test Name")
with col_c2:
    custom_price_input = st.number_input("Custom Test Fee", min_value=0.0, step=50.0, value=None, placeholder="Enter price...", key="c_price")
    custom_price = custom_price_input if custom_price_input is not None else 0.0

if custom_name.strip():
    total_fee += custom_price
    test_with_prices.append(f"{custom_name.strip()}({custom_price})")

st.info(f"### 💵 Total Bill Amount: {total_fee} BDT")

st.subheader("💵 Payment & Discounts")
col3, col4 = st.columns(2)
with col3:
    discount_amount_input = st.number_input("Discount Amount (৳)", min_value=0.0, value=None, placeholder="0.00")
    discount_amount = discount_amount_input if discount_amount_input is not None else 0.0
    advance_paid_input = st.number_input("Advance Paid (৳)", min_value=0.0, value=None, placeholder="0.00")
    advance_paid = advance_paid_input if advance_paid_input is not None else 0.0

net_payable = total_fee - discount_amount
due_amount = net_payable - advance_paid

with col4:
    st.metric("Discount Applied", f"{discount_amount} ৳")
    st.metric("Total Due Amount", f"{due_amount} ৳")

# --- 5. Database Save & Auto Redirect ---
submit_button = st.button("💾 Save Bill and Go to Print", use_container_width=True)

if submit_button:
    if not patient_name or not test_with_prices:
        st.error("❌ Patient Name and at least one test fee are required!")
    elif selected_doctor_setup == "Other" and not doctor_text:
        st.error("❌ Please enter the new doctor's details!")
    else:
        tests_data_str = ", ".join(test_with_prices)
        
        if "doctor_text" in locals() and doctor_text.strip():
            try:
                c.execute("INSERT OR IGNORE INTO doctors_list (doc_name) VALUES (?)", (doctor_text.strip(),))
                conn.commit()
            except Exception:
                pass
                
        if custom_name.strip():
            try:
                c.execute("INSERT OR IGNORE INTO custom_tests_list (test_name) VALUES (?)", (custom_name.strip(),))
                conn.commit()
            except Exception:
                pass
                
        # কলাম সাপোর্ট এরর এড়াতে ট্রাই-ক্যাচ দিয়ে ফ্লেক্সিবল সেভ মেথড
        success_save = False
        try:
            c.execute("""INSERT INTO billing_records 
                (patient_name, age, phone, selected_tests, total_amount, discount, advance, due, date, doctor_name, created_by) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, date('now'), ?, ?)""", 
                (patient_name, age, phone, tests_data_str, total_fee, discount_amount, advance_paid, due_amount, selected_doctor_setup, current_user))
            st.session_state.last_invoice_id = c.lastrowid
            conn.commit()
            success_save = True
        except sqlite3.OperationalError:
            try:
                c.execute("""INSERT INTO billing_records 
                    (patient_name, age, phone, selected_tests, total_amount, discount_amount, advance, due, date, doctor_name, created_by) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, date('now'), ?, ?)""", 
                    (patient_name, age, phone, tests_data_str, total_fee, discount_amount, advance_paid, due_amount, selected_doctor_setup, current_user))
                st.session_state.last_invoice_id = c.lastrowid
                conn.commit()
                success_save = True
            except Exception as final_err:
                st.error(f"❌ Database Error: {final_err}")
        except Exception as e:
            st.error(f"❌ Database Error: {e}")

        if success_save:
