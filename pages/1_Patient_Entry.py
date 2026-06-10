import streamlit as st
import sqlite3
from datetime import datetime

# ১. সিকিউরিটি চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

# ২. ডাটাবেজ কানেকশন ও টেবিলসমূহ তৈরি
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# পেশেন্ট বিলের টেবিল
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

# 📌 নতুন টেস্ট লিস্ট এবং প্রাইস রাখার মাস্টার টেবিল
c.execute("""
CREATE TABLE IF NOT EXISTS diagnostic_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT UNIQUE,
    price REAL
)
""")
conn.commit()

# ডাটাবেজে যদি কোনো টেস্ট না থাকে, তবে শুরুর জন্য কিছু টেস্ট অটোমেটিক ঢুকিয়ে দেওয়া
c.execute("SELECT COUNT(*) FROM diagnostic_tests")
if c.fetchone()[0] == 0:
    sample_tests = [
        ("Urine Pregnancy Test (HCG)", 200.0),
        ("AFP (Alpha Fetoprotein)", 1200.0),
        ("Blood Sugar (RBS / Fasting)", 200.0),
        ("Anti-HCV", 600.0),
        ("CBC (Complete Blood Count)", 400.0),
        ("Lipid Profile", 1000.0),
        ("Serum Creatinine", 300.0),
        ("S. Bilirubin", 250.0),
        ("Ultrasonography (USG)", 800.0),
        ("X-Ray Chest", 500.0)
    ]
    c.executemany("INSERT OR IGNORE INTO diagnostic_tests (test_name, price) VALUES (?, ?)", sample_tests)
    conn.commit()

# ডাটাবেজ থেকে সব টেস্টের নাম ও দামের ডিকশনারি তৈরি করা (এখানে ২০০টি টেস্ট থাকলেও অটোমেটিক চলে আসবে)
c.execute("SELECT test_name, price FROM diagnostic_tests")
test_prices = {row[0]: row[1] for row in c.fetchall()}

st.title("📝 টেস্ট এবং বিলিং সেকশন")

# এডমিনদের জন্য নতুন টেস্ট ডাটাবেজে যোগ করার একটি গোপন/আলাদা অপশন (Sidebar-এ)
with st.sidebar.expander("➕ নতুন টেস্ট ও দাম যোগ করুন"):
    new_test_name = st.text_input("টেস্টের নাম:")
    new_test_price = st.number_input("টেস্টের মূল্য (টাকা):", min_value=0.0, step=50.0)
    if st.button("ডাটাবেজে সেভ করুন"):
        if new_test_name:
            try:
                c.execute("INSERT INTO diagnostic_tests (test_name, price) VALUES (?, ?)", (new_test_name.strip(), new_test_price))
                conn.commit()
                st.success(f"✅ {new_test_name} যোগ করা হয়েছে!")
                st.rerun()
            except:
                st.error("⚠️ এই টেস্টটি অলরেডি ডাটাবেজে আছে।")

# মূল পেশেন্ট ফরম
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

# ডাটাবেজে থাকা সব টেস্ট এখানে ড্রপডাউনে দেখাবে
selected_tests = st.multiselect("টেস্ট সিলেক্ট করুন (Description):", list(test_prices.keys()))

# লাইভ টোটাল ফি হিসাব করা
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

if submit_button:
    if not name or not selected_tests:
        st.error("⚠️ পেশেন্টের নাম এবং অন্তত একটি টেস্ট সিলেক্ট করা বাধ্যতামূলক!")
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        tests_str = ", ".join(selected_tests)
        
        c.execute("""
            INSERT INTO billing_records (patient_name, age, phone, doctor, selected_tests, total_amount, discount_percent, net_paid, due_amount, billing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, age, phone, doctor, tests_str, total_fee, discount_pct, advance_paid, due_amount, current_date))
        conn.commit()
        
        st.session_state.last_invoice_id = c.lastrowid
        st.success("✅ সফলভাবে ডাটা সেভ হয়েছে! প্রিন্ট পেজে নিয়ে যাওয়া হচ্ছে...")
        st.switch_page("pages/3_Print_Receipt.py")

conn.close()
