import sys
import os
import streamlit as st
import sqlite3
import datetime
from datetime import datetime

# ১. গ্লোবাল পাথ সেটআপ ও সাইডবার লোড
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sidebar_monitor import show_live_sidebar

# ২. সাইডবার শো করা
show_live_sidebar()

# ৩. সিকিউরিটি চেক
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("অনধিকার প্রবেশাধিকার! দয়া করে ড্যাশবোর্ড থেকে লগইন করুন।")
    st.stop()

# ৪. আধুনিক ডার্ক মোড এবং লাইভ ঘরের নতুন কালার হাইলাইট করার কাস্টম CSS
st.markdown("""
    <style>
    /* মূল অ্যাপ ব্যাকগ্রাউন্ড */
    .stApp {
        background-color: #0b131f !important;
        color: #e2e8f0 !important;
    }
    
    /* লেবেল বা লেখার শিরোনামের কালার */
    .stApp label {
        color: #38bdf8 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
    
    /* সাইডবার ডার্ক থিম */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* ইনপুট বক্স ডিজাইন */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #18263c !important;
        color: #ffffff !important;
        border: 1px solid #2d3f5d !important;
        border-radius: 8px !important;
        padding: 10px !important;
        height: 44px !important;
    }
    
    /* ইনপুট বক্সে ক্লিক করলে গ্লো ইফেক্ট */
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #0284c7 !important;
        box-shadow: 0 0 10px rgba(2, 132, 199, 0.4) !important;
    }
    
    /* 🎨 লাইভ দেখার ঘরের জন্য বিশেষ গ্লোয়িং ব্যাকগ্রাউন্ড ও নিয়ন টেক্সট কালার */
    [data-testid="stMetricBlock"] {
        background-color: #16253b !important;
        border: 1px solid #0ea5e9 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.15) !important;
    }
    [data-testid="stMetricValue"] {
        color: #22c55e !important;
        font-weight: bold !important;
    }
    [data-testid="stMetricLabel"] {
        color: #38bdf8 !important;
    }
    
    /* সেভ বাটনের স্টাইল */
    .stButton button {
        background-color: #0284c7 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 30px !important;
        font-weight: bold !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #0369a1 !important;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.6) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ৫. ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# টেবিল তৈরি (যদি না থাকে)
c.execute("""
CREATE TABLE IF NOT EXISTS billing_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    age INTEGER,
    phone TEXT,
    doctor TEXT,
    selected_tests TEXT,
    total_amount REAL,
    discount_percent REAL,
    net_paid REAL,
    due_amount REAL,
    billing_date TEXT
)""")

c.execute("""
CREATE TABLE IF NOT EXISTS doctors_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_name TEXT UNIQUE
)""")

c.execute("""
CREATE TABLE IF NOT EXISTS custom_tests_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT UNIQUE
)""")
conn.commit()

# ডিফল্ট ডাক্তার ডেটা ইনসার্ট লজিক
c.execute("SELECT COUNT(*) FROM doctors_list")
if c.fetchone() == 0:
    default_docs = [("ডা. সাইদুল ইসলাম",), ("ডা. আসাদুর রহমান",)]
    c.executemany("INSERT INTO doctors_list (doc_name) VALUES (?)", default_docs)
    conn.commit()

# ডিফল্ট টেস্ট ডেটা ইনসার্ট লজিক
c.execute("SELECT COUNT(*) FROM custom_tests_list")
if c.fetchone() == 0:
    default_tests = [
        ("CBC",), ("ESR",), ("TC.DC",), ("HB%",), ("Platelet Count",), ("MP",), ("BT/CT",), ("C/E Count",),
        ("Widal",), ("Aso Titre",), ("CRP",), ("RA/RF",), ("HBs Ag (Screen Test)",), ("TPHA",), ("VDRL",),
        ("Group & Rh Factor",), ("Mantoux-Test (M.T)",), ("Triple Antigen",), ("W.Fever",), ("HIV",), ("HCV",),
        ("Random Blood Sugar (RBS)",), ("Fasting Blood Sugar (FBS)",), ("2hr. After Breakfast",),
        ("Blood Urea",), ("Cholesterol",), ("TG (Triglycerides)",), ("S.GPT (ALT)",), ("S.GOT (AST)",),
        ("Bilirubin Total",), ("Lipid Profile",), ("Serum Creatinine",), ("Uric Acid",),
        ("Urine Pregnancy Test (PT)",), ("Urine R/E",), ("Stool R/E",),
        ("USG Whole Abdomen",), ("USG Upper Abdomen",), ("USG Lower Abdomen",), ("USG KUB",), ("USG Pregnancy Profile",),
        ("X-Ray Chest",), ("X-Ray PNS",), ("X-Ray Cervical Spine",), ("X-Ray L/S Spine",), ("X-Ray Knee B/V",)
    ]
    c.executemany("INSERT INTO custom_tests_list (test_name) VALUES (?)", default_tests)
    conn.commit()

# ডাটাবেজ থেকে টেস্টের তালিকা লোড করা
c.execute("SELECT test_name FROM custom_tests_list")
available_tests = [row[0] for row in c.fetchall()] # Tuple থেকে টেক্সট কনভার্সন ফিক্স
available_tests.sort()

# মূল ইউজার ইন্টারফেস
st.title("📝 টেস্ট এবং বিলিং সেকশন")
st.subheader("পেশেন্ট ইনফরমেশন")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("পেশেন্টের নাম (Name of the PT) *")
    phone = st.text_input("মোবাইল নাম্বার (Phone) *")
with col2:
    age = st.number_input("বয়স (Age)", min_value=1, max_value=120, value=25)

# ডাটাবেজ থেকে ডাক্তারদের লিস্ট লোড
c.execute("SELECT doc_name FROM doctors_list")
db_doctors = [row[0] for row in c.fetchall()] # Tuple থেকে টেক্সট কনভার্সন ফিক্স

doctor_options = db_doctors + ["অন্যান্য"]
selected_doctor_setup = st.selectbox("ডাক্তার সিলেক্ট করুন (Refd By)", doctor_options)

if selected_doctor_setup == "অন্যান্য":
    doctor = st.text_input("নতুন ডাক্তারের নাম ও ডিগ্রি এখানে লিখুন: *")
else:
    doctor = selected_doctor_setup

st.markdown("---")
st.subheader("টেস্ট সিলেকশন ও লাইভ রেট এন্ট্রি")

# মাল্টিসিলেক্ট ড্রপডাউন
selected_tests = st.multiselect("তালিকা থেকে টেস্ট সিলেক্ট করুন:", available_tests)

test_with_prices = []
total_fee = 0.0

if selected_tests:
    st.markdown("##### 📌 নির্বাচিত টেস্টসমূহের দাম এখানে দেখে নিন:")
    for test in selected_tests:
        # value=None দেওয়ার কারণে ০.০০ কাটার ঝামেলা থাকবে না
        price_input = st.number_input(
            f"ফি (৳) -- {test}:", 
            min_value=0.0, 
            step=50.0, 
            value=None, 
            placeholder="ফি লিখুন...", 
            key=f"price_{test}"
        )
        price = price_input if price_input is not None else 0.0
        total_fee += price
        test_with_prices.append(f"{test}({price})")

st.markdown("##### ➕ তালিকা বহির্ভূত কাস্টম টেস্ট (ঐচ্ছিক)")
col_c1, col_c2 = st.columns(2)
with col_c1:
    custom_name = st.text_input("কাস্টম টেস্টের নাম:")
with col_c2:
    custom_price_input = st.number_input("কাস্টম টেস্টের মূল্য:", min_value=0.0, step=50.0, value=None, placeholder="মূল্য লিখুন...")
    custom_price = custom_price_input if custom_price_input is not None else 0.0

if custom_name.strip():
    total_fee += custom_price
    test_with_prices.append(f"{custom_name.strip()}({custom_price})")

st.info(f"ℹ️ লাইভ মোট বিল (টোটাল টেস্ট ফি): {total_fee} টাকা")
st.markdown("---")

st.subheader("পেমেন্ট ও ডিসকাউন্ট")
col3, col4 = st.columns(2)

with col3:
    # ফ্ল্যাট ডিসকাউন্ট টাকা ইনপুট (বক্স খালি থাকবে)
    discount_amount_input = st.number_input("মোট ডিসকাউন্ট (Discount Amount ৳)", min_value=0.0, value=None, step=10.0, placeholder="ডিসকাউন্ট লিখুন...")
    discount_amount = discount_amount_input if discount_amount_input is not None else 0.0
    
    advance_paid_input = st.number_input("অগ্রিম পরিশোধ (Advance Paid)", min_value=0.0, value=None, placeholder="অগ্রিম টাকা লিখুন...")
    advance_paid = advance_paid_input if advance_paid_input is not None else 0.0

# গাণিতিক সূত্র
net_payable = total_fee - discount_amount
due_amount = net_payable - advance_paid

with col4:
    st.metric("ডিসকাউন্ট প্রণয় (টাকা)", f"{discount_amount} ৳")
    st.metric("মোট বাকি টাকা (Due)", f"{due_amount} ৳")

st.markdown("---")
submit_button = st.button("Save Bill and Go to Print (বিল সেভ করুন)")

if submit_button:
    if not name or not test_with_prices:
        st.error("🚨 পেশেন্টের নাম এবং অন্তত একটি টেস্টের নাম দেওয়া বাধ্যতামূলক!")
    elif selected_doctor_setup == "অন্যান্য" and not doctor.strip():
        st.error("🚨 নতুন ডাক্তারের নাম টেক্সট বক্সে লিখুন!")
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        tests_data_str = ", ".join(test_with_prices)
        
        if selected_doctor_setup == "অন্যান্য":
            try:
                c.execute("INSERT OR IGNORE INTO doctors_list (doc_name) VALUES (?)", (doctor.strip(),))
                conn.commit()
            except:
                pass
                
        if custom_name.strip():
            try:
                c.execute("INSERT OR IGNORE INTO custom_tests_list (test_name) VALUES (?)", (custom_name.strip(),))
                conn.commit()
            except:
                pass
                
        # ডাটাবেজে সেভ করার ফাইনাল কোড
        try:
            c.execute("""
            INSERT INTO billing_records (patient_name, age, phone, doctor, selected_tests, total_amount, discount_percent, net_paid, due_amount, billing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(name), int(age), str(phone), str(doctor), str(tests_data_str), float(total_fee), float(discount_amount), float(advance_paid), float(due_amount), str(current_date)))
            conn.commit()
            
            st.session_state.last_invoice_id = c.lastrowid
            st.success("🎉 বিল সফলভাবে সংরক্ষিত হয়েছে! প্রিন্ট পেজে নেওয়া হচ্ছে...")
            st.switch_pages("pages/3_Print_Receipt.py")
        except Exception as e:
            st.error(f"ডাটাবেজ এরর: {e}")

conn.close()
