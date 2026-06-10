import streamlit as st
import sqlite3
from datetime import datetime

# ১. সিকিউরিটি চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

# ২. ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

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
)
""")
conn.commit()

st.title("📝 টেস্ট এবং বিলিং সেকশন")

st.subheader("পেশেন্ট ইনফরমেশন")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("পেশেন্টের নাম (Name of the PT) *")
    phone = st.text_input("মোবাইল নম্বর (Phone)")
with col2:
    age = st.number_input("বয়স (Age)", min_value=1, max_value=120, value=25)
    doctor = st.selectbox("ডাক্তার সিলেক্ট করুন (Refd By)", ["ডা. সাইদুল ইসলাম", "অন্যান্য"])

st.markdown("---")
st.subheader("টেস্ট সিলেকশন")

test_prices = {
    "Urine Pregnancy Test (HCG)": 200.0,
    "AFP (Alpha Fetoprotein)": 1200.0,
    "Blood Sugar (RBS / Fasting)": 200.0,
    "Anti-HCV": 600.0
}

selected_tests = st.multiselect("টেস্ট সিলেক্ট করুন (Description):", list(test_prices.keys()))
total_fee = sum(test_prices[test] for test in selected_tests)
st.info(f"📋 লাইভ টোটাল ফি: {total_fee} টাকা")

st.markdown("---")
st.subheader("পেমেন্ট ও ডিসকাউন্ট")
col3, col4 = st.columns(2)
with col3:
    discount_pct = st.number_input("ডিসকাউন্ট (Discount %)", min_value=0.0, max_value=100.0, value=0.0)
    advance_paid = st.number_input("অগ্রিম পরিশোধ (Advance Paid)", min_value=0.0, value=0.0)

discount_amount = (total_fee * discount_pct) / 100.0
net_payable = total_fee - discount_amount
due_amount = net_payable - advance_paid

with col4:
    st.metric("ডিসকাউন্ট প্রদেয় (টাকা)", f"{discount_amount} ৳")
    st.metric("মোট বাকি টাকা (Due)", f"{due_amount} ৳")

st.markdown("---")
submit_button = st.button("Save Bill and Go to Print (ডাটা সেভ করুন)")

# ডাটা সেভ লজিক
if submit_button:
    if not name or not selected_tests:
        st.error("⚠️ পেশেন্টের নাম এবং অন্তত একটি টেস্ট সিলেক্ট করা বাধ্যতামূলক!")
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        tests_str = ", ".join(selected_tests)
        
        # ডাটা সেভ করা
        c.execute("""
            INSERT INTO billing_records (patient_name, age, phone, doctor, selected_tests, total_amount, discount_percent, net_paid, due_amount, billing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, age, phone, doctor, tests_str, total_fee, discount_pct, advance_paid, due_amount, current_date))
        conn.commit()
        
        # ৩. ম্যাজিক: সর্বশেষ আইডির ট্র্যাকিং রাখা এবং সরাসরি প্রিন্ট পেজে পাঠিয়ে দেওয়া
        st.session_state.last_invoice_id = c.lastrowid
        st.success("✅ সফলভাবে ডাটা সেভ হয়েছে! প্রিন্ট পেজে নিয়ে যাওয়া হচ্ছে...")
        
        # স্ট্রিমলিটের মাধ্যমে স্বয়ংক্রিয়ভাবে ৩ নম্বর প্রিন্ট পেজে পাঠানো
        st.switch_page("pages/3_Print_Receipt.py")

conn.close()
