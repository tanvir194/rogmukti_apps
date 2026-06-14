import sys
import os
import streamlit as st
import sqlite3
from datetime import datetime

# ১. গ্লোবাল পাথ সেটআপ ও সাইডবার লোড
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from sidebar_monitor import show_live_sidebar
    show_live_sidebar()
except Exception:
    pass

# --- ডাটাবেজ কানেকশন ---
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# প্রয়োজনীয় টেবিল তৈরি ও কলাম নিশ্চিতকরণ
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

# যদি আগের ডেটাবেজে created_by কলাম না থাকে, তবে তা যোগ করার চেষ্টা করবে
try:
    c.execute("ALTER TABLE billing_records ADD COLUMN created_by TEXT")
    conn.commit()
except Exception:
    pass

c.execute("""CREATE TABLE IF NOT EXISTS doctors_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    doc_name TEXT UNIQUE)""")

c.execute("""CREATE TABLE IF NOT EXISTS custom_tests_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    test_name TEXT UNIQUE)""")

# ইউজার টেবিল (যদি না থাকে) এবং ডিফল্ট অ্যাডমিন ক্রিয়েশন
c.execute("""CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY, 
    password TEXT,
    role TEXT DEFAULT 'staff')""")
c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
conn.commit()

# --- ২. সিকিউর লগইন সিস্টেম ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in or 'username' not in st.session_state:
    st.markdown("<h2 style='text-align: center; color: #ff4b4b;'>🔑 রিসিট কাউন্টার লগইন</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username_input = st.text_input("ইউজারনেম (Username)").strip()
        password_input = st.text_input("পাসওয়ার্ড (Password)", type="password")
        login_btn = st.form_submit_button("লগইন করুন", use_container_width=True)
        
        if login_btn:
            if username_input and password_input:
                c.execute("SELECT password, role FROM users WHERE username = ?", (username_input,))
                user_data = c.fetchone()
                
                if user_data and user_data[0] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.session_state.role = user_data[1]
                    st.success(f"🎉 স্বাগতম {username_input}! সিস্টেমে প্রবেশ করা হচ্ছে...")
                    st.rerun()
                else:
                    st.error("❌ ভুল ইউজারনেম অথবা পাসওয়ার্ড!")
            else:
                st.warning("⚠️ দয়া করে ইউজারনেম এবং পাসওয়ার্ড দুটিই লিখুন।")
    st.stop()

# --- ৩. কাস্টম CSS ডিজাইন ---
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

# লগইন ইউজারের নাম ও মারকুই প্রদর্শন
current_user = st.session_state.get('username', 'Unknown')
st.markdown(f"<div style='text-align: right; color: #8b949e; font-weight: bold;'>👤 বর্তমান ইউজার: <span style='color: #58a6ff;'>{current_user}</span></div>", unsafe_allow_html=True)
st.markdown("<marquee style='color: #ff7b72; font-weight: bold;'>⚠️ সতর্কতা: নতুন পেশেন্ট এন্ট্রি ও বিল তৈরি করার সময় তথ্যগুলো সতর্কতার সাথে যাচাই করে সাবমিট করুন।</marquee>", unsafe_allow_html=True)

# ডাক্তার লিস্ট লোড করা
c.execute("SELECT doc_name FROM doctors_list")
db_doctors = [row[0] for row in c.fetchall() if row]
doctor_options = db_doctors + ["অন্যান্য"]

# --- টেস্ট লিস্ট লোড করা ---
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

# --- ৪. ফরম ডিজাইন ও ইনপুট সেকশন ---
st.title("🏥 রোগ মুক্তি এক্স-রে এন্ড ডিজিটাল ল্যাব")
st.subheader("📋 পেশেন্ট ইনফরমেশন")

col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("পেশেন্টের নাম (Name of the PT) *")
    phone = st.text_input("মোবাইল নাম্বার (Phone) *")
with col2:
    age = st.number_input("বয়স (Age)", min_value=1, max_value=120, value=25)
    selected_doctor_setup = st.selectbox("রেফারেন্স ডাক্তার (Refd By)*", doctor_options)

if selected_doctor_setup == "অন্যান্য":
    doctor_text = st.text_input("নতুন ডাক্তারের নাম ও ডিগ্রি এখানে লিখুন: *")
    if doctor_text:
        selected_doctor_setup = doctor_text.strip()

st.subheader("🔬 টেস্ট সিলেকশন ও প্রাইস (ফি)")
selected_tests = st.multiselect("তালিকা থেকে টেস্ট সিলেক্ট করুন:", available_tests)

test_with_prices = []
total_fee = 0.0

if selected_tests:
    st.markdown("##### 💰 নির্বাচিত টেস্টসমূহের ফি এখানে দিন:")
    for test in selected_tests:
        price_input = st.number_input(f"({test}) এর ফি:", min_value=0.0, step=50.0, value=None, placeholder="ফি লিখুন...", key=f"p_{test}")
        price = price_input if price_input is not None else 0.0
        total_fee += price
        test_with_prices.append(f"{test}({price})")

st.markdown("##### ➕ তালিকায় না থাকা কোনো এক্সট্রা টেস্ট (ঐচ্ছিক):")
col_c1, col_c2 = st.columns(2)
with col_c1:
    custom_name = st.text_input("কাস্টম টেস্টের নাম *")
with col_c2:
    custom_price_input = st.number_input("কাস্টম টেস্টের ফি", min_value=0.0, step=50.0, value=None, placeholder="ফি লিখুন...", key="c_price")
    custom_price = custom_price_input if custom_price_input is not None else 0.0

if custom_name.strip():
    total_fee += custom_price
    test_with_prices.append(f"{custom_name.strip()}({custom_price})")

st.info(f"### 💵 মোট বিলের পরিমাণ (টোটাল ফি): {total_fee} টাকা")

st.subheader("💵 পেমেন্ট ও ডিসকাউন্ট")
col3, col4 = st.columns(2)
with col3:
    discount_amount_input = st.number_input("ছাড়/ডিসকাউন্ট (Discount Amount ৳)", min_value=0.0, value=None, placeholder="০.০০")
    discount_amount = discount_amount_input if discount_amount_input is not None else 0.0
    
    advance_paid_input = st.number_input("অগ্রিম পরিশোধ (Advance Paid ৳)", min_value=0.0, value=None, placeholder="০.০০")
    advance_paid = advance_paid_input if advance_paid_input is not None else 0.0

net_payable = total_fee - discount_amount
due_amount = net_payable - advance_paid

with col4:
    st.metric("ডিসকাউন্ট প্রাপ্ত (টাকা)", f"{discount_amount} ৳")
    st.metric("মোট বাকি টাকা (Due)", f"{due_amount} ৳")

# --- ৫. ডাটাবেজে সাবমিট লজিক ---
submit_button = st.button("💾 Save Bill and Go to Print (বিল সেভ করুন)")

if submit_button:
    if not patient_name or not test_with_prices:
        st.error("❌ পেশেন্টের নাম এবং অন্তত একটি টেস্টের ফি দেওয়া বাধ্যতামূলক!")
    elif selected_doctor_setup == "অন্যান্য" and not doctor_text:
        st.error("❌ দয়া করে নতুন ডাক্তারের নাম ও ডিগ্রীটি উল্লেখ করুন!")
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
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
                
        try:
            c.execute("""INSERT INTO billing_records 
                (patient_name, age, phone, selected_tests, total_amount, discount, advance, due, date, doctor_name, created_by) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                (patient_name, age, phone, tests_data_str, total_fee, discount_amount, advance_paid, due_amount, current_date, selected_doctor_setup, current_user))
            
            st.session_state.last_invoice_id = c.lastrowid
            conn.commit()
            st.success("🎉 বিল সফলভাবে সংরক্ষিত হয়েছে! প্রিন্ট পেজে নেওয়া হচ্ছে...")
            st.switch_page("pages/3_Print_Receipt.py")
            
        except sqlite3.OperationalError:
            try:
                c.execute("""INSERT INTO billing_records 
                    (patient_name, age, phone, selected_tests, total_amount, discount_amount, advance, due, date, doctor_name, created_by) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                    (patient_name, age, phone, tests_data_str, total_fee, discount_amount, advance_paid, due_amount, current_date, selected_doctor_setup, current_user))
