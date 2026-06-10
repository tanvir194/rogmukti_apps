import streamlit as st
import sqlite3
from datetime import datetime

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# টেবিল তৈরি (ফিক্সড স্ট্রাকচার)
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

c.execute("""
CREATE TABLE IF NOT EXISTS diagnostic_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT UNIQUE,
    price REAL
)
""")
conn.commit()

c.execute("SELECT COUNT(*) FROM diagnostic_tests")
count_result = c.fetchone()
test_count = count_result[0] if count_result else 0

if test_count < 15:
    c.execute("DELETE FROM diagnostic_tests")
    galachipa_official_tests = [
        ("(CBC), ESR", 400.0), ("TC.DC", 250.0), ("HB%", 250.0), ("ESR", 200.0),
        ("Platelet Count", 300.0), ("MP", 200.0), ("BT/CT", 350.0), ("C/E Count", 250.0),
        ("Widal", 450.0), ("Aso Titre", 450.0), ("CRP", 450.0), ("RA/RF", 450.0),
        ("HBs Ag (Screen Test)", 450.0), ("TPHA", 450.0), ("VDRL", 400.0),
        ("Group & Rh Factor", 200.0), ("Mantaux-Test (M.T)", 250.0), ("Triple Antigen", 500.0),
        ("R.Fever", 450.0), ("HIV", 500.0), ("HCV", 500.0), ("TB (ICT)", 750.0),
        ("Malaria. pf/pv", 700.0), ("H. Pylori", 850.0), ("Fallaria (ICT)", 750.0),
        ("Dengue NS1. IGG/IgM", 300.0),
        ("T3", 1200.0), ("T4", 1200.0), ("FT3", 900.0), ("FT4", 900.0), ("TSH", 1100.0),
        ("HbA1c", 1500.0), ("Prolactin", 1200.0), ("S. IgE", 1500.0), ("S.IgE (Device Test)", 700.0),
        ("Random Blood Sugar (RBS)", 200.0), ("Fasting Blood Sugar (FBS)", 200.0),
        ("2hr. After Breakfast", 200.0), ("2hr. After 75gm Glucose", 200.0), ("O.G.T.T", 500.0),
        ("Blood Urea", 400.0), ("Cholesterol", 350.0), ("HDL", 400.0), ("TG (Triglycerides)", 350.0),
        ("LDL", 300.0), ("S.GPT (ALT)", 500.0), ("S.GOT (AST)", 500.0), ("Bilirubin Total", 350.0),
        ("Lipid Profile", 1000.0), ("Bilirubin Direct/Indirect", 450.0), ("Serum Creatinine", 400.0),
        ("Uric Acid", 400.0), ("Amylase", 700.0), ("Calcium", 600.0),
        ("Urine Pregnancy Test (PT)", 200.0), ("Urine R/E", 250.0),
        ("Stool R/E", 400.0), ("Stool OBT", 400.0),
        ("USG Whole Abdomen", 1000.0), ("USG Upper Abdomen", 800.0), ("USG Lower Abdomen", 800.0),
        ("USG KUB", 1000.0), ("USG Pregnancy Profile", 800.0), ("USG Breast", 1200.0),
        ("X-Ray Chest", 500.0), ("X-Ray PNS", 500.0), ("X-Ray Maxilla", 500.0), ("X-Ray Nasopharynx", 550.0),
        ("X-Ray Abdomen A/P", 500.0), ("X-Ray Cervical Spine", 600.0), ("X-Ray Plane X-Ray Abdomen", 500.0),
        ("X-Ray Mastoid Towns View", 500.0), ("X-Ray Skull", 600.0), ("X-Ray Pelvic", 500.0),
        ("X-Ray Mandible B/V", 600.0), ("X-Ray KUB", 500.0), ("X-Ray D/S Spine", 600.0),
        ("X-Ray L/S Spine", 600.0), ("X-Ray Foot B/V", 500.0), ("X-Ray Knee B/V", 550.0),
        ("X-Ray Elbow B/V", 500.0), ("X-Ray Shoulder Joint B/V", 550.0), ("X-Ray Hip Joint", 500.0)
    ]
    c.executemany("INSERT OR IGNORE INTO diagnostic_tests (test_name, price) VALUES (?, ?)", galachipa_official_tests)
    conn.commit()

c.execute("SELECT test_name, price FROM diagnostic_tests ORDER BY test_name ASC")
test_prices = {row[0]: row[1] for row in c.fetchall()}

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

selected_tests = st.multiselect("তালিকা থেকে টেস্ট সিলেক্ট করুন (Description):", list(test_prices.keys()))
regular_fee = sum(test_prices[test] for test in selected_tests)

st.markdown("#### ➕ তালিকা বহির্ভূত কাস্টম টেস্ট যোগ করুন (ঐচ্ছিক)")
col_c1, col_c2 = st.columns(2)
with col_c1:
    custom_test_name = st.text_input("কাস্টম টেস্টের নাম লিখুন:", key="custom_name")
with col_c2:
    custom_test_price = st.number_input("কাস্টম টেস্টের দাম (টাকা):", min_value=0.0, step=50.0, key="custom_price")

total_fee = regular_fee + custom_test_price
st.info(f"📋 লাইভ মোট বিল (টোটাল ফি): {total_fee} টাকা")

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
    if not name or (not selected_tests and not custom_test_name.strip()):
        st.error("⚠️ পেশেন্টের নাম এবং অন্তত একটি টেস্ট দেওয়া বাধ্যতামূলক!")
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        all_tests_list = list(selected_tests)
        if custom_test_name.strip():
            all_tests_list.append(custom_test_name.strip())
        tests_str = ", ".join(all_tests_list)
        
        c.execute("""
            INSERT INTO billing_records (patient_name, age, phone, doctor, selected_tests, total_amount, discount_percent, net_paid, due_amount, billing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, age, phone, doctor, tests_str, total_fee, discount_pct, advance_paid, due_amount, current_date))
        conn.commit()
        
        if custom_test_name.strip():
            try:
                c.execute("INSERT OR IGNORE INTO diagnostic_tests (test_name, price) VALUES (?, ?)", (custom_test_name.strip(), custom_test_price))
                conn.commit()
            except:
                pass
        
        st.session_state.last_invoice_id = c.lastrowid
        st.success("✅ সফলভাবে ডাটা সেভ হয়েছে! প্রিন্ট পেজে নিয়ে যাওয়া হচ্ছে...")
        st.switch_page("pages/3_Print_Receipt.py")

conn.close()
