import sys
import os
import streamlit as st
import sqlite3
import datetime
from datetime import datetime

# ১. গ্লোবাল পাথ সেটআপ ও সাইডবার লোড
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from sidebar_monitor import show_live_sidebar
    show_live_sidebar()
except Exception:
    pass

# ২. সিকিউরিটি চেক
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ অননুমোদিত প্রবেশাধিকার! দয়া করে ড্যাশবোর্ড থেকে লগইন করুন তানভীর ভাই।")
    st.stop()

# ৩. কাস্টম CSS ডিজাইন
st.markdown("""
<style>
.stApp { background-color: #0b131f !important; color: #e2e8f0 !important; }
.stApp label { color: #38bdf8 !important; font-weight: 500 !important; font-size: 0.95rem !important; }
[data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #1e293b; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
.stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stMultiSelect div {
    background-color: #18263c !important; color: #ffffff !important; border: 1px solid #2d3f5d !important; border-radius: 8px !important; padding: 10px !important;
}
[data-testid="stMetricBlock"] { background-color: #16253b !important; border: 1px solid #0ea5e9 !important; border-radius: 10px !important; padding: 12px !important; }
[data-testid="stMetricValue"] { color: #22c55e !important; font-weight: bold !important; }
[data-testid="stMetricLabel"] { color: #38bdf8 !important; }
.stButton button { background-color: #0284c7 !important; color: white !important; border-radius: 8px !important; padding: 12px 30px !important; font-weight: bold !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

# ৪. স্বাগতম টেক্সট ও বড় স্ক্রলিং নোটিশ (Marquee)
st.markdown("""
<div style='text-align: center; margin-bottom: 15px;'>
    <h1 style='color: #ff5555; font-size: 38px; font-weight: 900; font-family: sans-serif; margin: 0;'>
        মো: তানভীর আহমেদ আপনাকে @স্বাগতম@।)
        দয়া করে সফটওয়ারে কোন সমস্যা হলে সাথে সাথে তানভীর ভাইকে কল করুন অন্য কোন চেষ্টা করবেন না।
    </h1>
</div>
<div style='background-color: #16253b; padding: 15px; border-radius: 8px; border: 2px solid #0ea5e9; margin-bottom: 25px;'>
    <marquee style='color: #f1f72a; font-size: 34px; font-weight: bold;'>
        👋 রোগমুক্তি ডায়াগনস্টিক অ্যান্ড ডিজিটাল ল্যাবে স্বাগতম! ⚠️ সতর্কর্তা: নতুন পেশেন্ট এন্ট্রি ও বিল তৈরি করার সময় তথ্যগুলো অনুগ্রহ করে বার বার চেক করে নিন যাতে কোন ভুল না হয়।
    </marquee>
</div>
""", unsafe_allow_html=True)

# ৫. ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS billing_records (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_name TEXT, age INTEGER, phone TEXT, doctor TEXT, selected_tests TEXT, total_amount REAL, discount_percent REAL, net_paid REAL, due_amount REAL, billing_date TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS doctors_list (id INTEGER PRIMARY KEY AUTOINCREMENT, doc_name TEXT UNIQUE)")
c.execute("CREATE TABLE IF NOT EXISTS custom_tests_list (id INTEGER PRIMARY KEY AUTOINCREMENT, test_name TEXT UNIQUE)")
conn.commit()

c.execute("SELECT COUNT(*) FROM doctors_list")
if c.fetchone()[0] == 0:
    c.executemany("INSERT INTO doctors_list (doc_name) VALUES (?)", [("ডাঃ সাইদুল ইসলাম",), ("ডাঃ আসাদুর রহমান",)])
    conn.commit()

try:
    c.execute("SELECT test_name FROM custom_tests_list")
    available_tests = [str(row[0]) for row in c.fetchall() if row]
except Exception:
    available_tests = []

default_laboratory_tests = ["CBC", "ESR", "TC.DC", "HB%", "Platelet Count", "MP", "BT/CT", "C/E Count", "Widal", "Aso Titre", "CRP", "RA/RF", "HBs Ag (Screen Test)", "TPHA", "VDRL", "Group & Rh Factor", "Mantoux-Test (M.T)", "Triple Antigen", "W.Fever", "HIV", "HCV", "Random Blood Sugar (RBS)", "Fasting Blood Sugar (FBS)", "2hr. After Breakfast", "Blood Urea", "Cholesterol", "TG (Triglycerides)", "S.GPT (ALT)", "S.GOT (AST)", "Bilirubin Total", "Lipid Profile", "Serum Creatinine", "Uric Acid", "Urine Pregnancy Test (PT)", "Urine R/E", "Stool R/E", "USG Whole Abdomen", "USG Upper Abdomen", "USG Lower Abdomen", "USG KUB", "USG Pregnancy Profile", "X-Ray Chest", "X-Ray PNS", "X-Ray Cervical Spine", "X-Ray L/S Spine", "X-Ray Knee B/V"]
for t_name in default_laboratory_tests:
    if t_name not in available_tests:
        available_tests.append(t_name)
available_tests.sort()

st.title("📝 টেস্ট এবং বিলিং সেকশন")
st.subheader("পেশেন্ট ইনফরমেশন")

col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("পেশেন্টের নাম (Name of the PT) *")
    phone = st.text_input("মোবাইল নাম্বার (Phone) *")
with col2:
    age = st.number_input("বয়স (Age)", min_value=1, max_value=120, value=25)

c.execute("SELECT doc_name FROM doctors_list")
db_doctors = [row[0] for row in c.fetchall()]
doctor_options = db_doctors + ["অন্যান্য"]
selected_doctor_setup = st.selectbox("রেফারেন্স ডাক্তার (Refd By)*", doctor_options)

doctor = st.text_input("নতুন ডাক্তারের নাম ও ডিগ্রি এখানে লিখুন: *") if selected_doctor_setup == "অন্যান্য" else selected_doctor_setup

st.markdown("---")
st.subheader("টেস্ট সিলেকশন ও লাইভ রেট এন্ট্রি")
selected_tests = st.multiselect("তালিকা থেকে টেস্ট সিলেক্ট করুন:", available_tests)

test_with_prices = []
total_fee = 0.0

if selected_tests:
    st.markdown("##### 📌 নির্বাচিত টেস্টসমূহের দাম এখানে লিখে দিন:")
    for test in selected_tests:
        price_input = st.number_input(f"💰 {test}:", min_value=0.0, step=50.0, value=None, placeholder="ফি লিখুন...", key=f"price_{test}")
        price = price_input if price_input is not None else 0.0
        total_fee += price
        test_with_prices.append(f"{test}({price})")

st.markdown("##### ➕ তালিকা বহির্ভূত কাস্টম টেস্ট (ঐচ্ছিক)")
col_c1, col_c2 = st.columns(2)
with col_c1:
    custom_name = st.text_input("কাস্টম টেস্টের নাম:")
with col_c2:
    custom_price_input = st.number_input("কাস্টম টেস্টের মূল্য:", min_value=0.0, step=50.0, value=None, placeholder="ফি...")
    custom_price = custom_price_input if custom_price_input is not None else 0.0

if custom_name.strip():
    total_fee += custom_price
    test_with_prices.append(f"{custom_name.strip()}({custom_price})")

st.info(f"💵 লাইভ মোট বিল (টোটাল টেস্ট ফি): {total_fee} টাকা")
st.markdown("---")

st.subheader("পেমেন্ট ও ডিসকাউন্ট")
col3, col4 = st.columns(2)
with col3:
    discount_amount_input = st.number_input("মোট ডিসকাউন্ট (Discount Amount ৳)", min_value=0.0, value=None, placeholder="৳...")
    discount_amount = discount_amount_input if discount_amount_input is not None else 0.0
    advance_paid_input = st.number_input("অগ্রিম পরিশোধ (Advance Paid)", min_value=0.0, value=None, placeholder="৳...")
    advance_paid = advance_paid_input if advance_paid_input is not None else 0.0

net_payable = total_fee - discount_amount
due_amount = net_payable - advance_paid

with col4:
    st.metric("ডিসকাউন্ট প্রাপ্য (টাকা)", f"{discount_amount} ৳")
    st.metric("মোট বাকি টাকা (Due)", f"{due_amount} ৳")

st.markdown("---")
submit_button = st.button("Save Bill and Go to Print (বিল সেভ করুন)")

if submit_button:
    if not patient_name or not test_with_prices:
        st.error("🚨 পেশেন্টের নাম এবং অন্তত একটি টেস্টের নাম দেওয়া বাধ্যতামূলক!")
    elif selected_doctor_setup == "অন্যান্য" and not doctor.strip():
        st.error("🚨 নতুন ডাক্তারের নাম দেওয়া বাধ্যতামূলক!")
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        tests_data_str = ", ".join(test_with_prices)
        if selected_doctor_setup == "অন্যান্য":
            try:
                c.execute("INSERT OR IGNORE INTO doctors_list (doc_name) VALUES (?)", (doctor.strip(),))
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
            c.execute("INSERT INTO billing_records (patient_name, age, phone, doctor, selected_tests, total_amount, discount_percent, net_paid, due_amount, billing_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (patient_name, int(age), str(phone), str(doctor), str(tests_data_str), float(total_fee), float(discount_amount), float(advance_paid), float(due_amount), str(current_date)))
            conn.commit()
            st.session_state.last_invoice_id = c.lastrowid
            st.success("🎉 বিল সফলভাবে সংরক্ষিত হয়েছে! প্রিন্ট পেজে নেওয়া হচ্ছে...")
            st.switch_page("pages/3_Print_Receipt.py")
        except Exception as e:
            st.error(f"ডাটাবেজ এরর: {e}")
conn.close()
