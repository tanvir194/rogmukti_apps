import streamlit as st
import sqlite3
import sys
sys.path.append(".")
from sidebar_monitor import show_live_sidebar
show_live_sidebar()

# ৩. সিকিউরিটি চেক (নিরাপত্তা ব্যবস্থা)
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

# ৪. ডাটাবেস কানেকশন (নিরাপত্তা পাস হলে এটি চলবে)
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# 1. Creating a database table (for patient bills)
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

#2. Create a separate dynamic table for doctor names
c.execute("""
CREATE TABLE IF NOT EXISTS doctors_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_name TEXT UNIQUE
)
""")

# ৩. 🌟 টেস্টের নামের জন্য আলাদা ডাইনামিক টেবিল তৈরি (নতুন ফিচার)
c.execute("""
CREATE TABLE IF NOT EXISTS custom_tests_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT UNIQUE
)
""")
conn.commit()

# Setting some default doctor names if the table is empty for the first time
c.execute("SELECT COUNT(*) FROM doctors_list")
if c.fetchone()[0] == 0:
    default_docs = [("ডা. সাইদুল ইসলাম",), ("ডা. আবদুর রহমান",)]
    c.executemany("INSERT INTO doctors_list (doc_name) VALUES (?)", default_docs)
    conn.commit()

# If the table is empty for the first time, insert the names of all your default tests into this dynamic table.
c.execute("SELECT COUNT(*) FROM custom_tests_list")
if c.fetchone()[0] == 0:
    default_tests = [
        ("(CBC), ESR",), ("TC.DC",), ("HB%",), ("ESR",), ("Platelet Count",), ("MP",), ("BT/CT",), ("C/E Count",),
        ("Widal",), ("Aso Titre",), ("CRP",), ("RA/RF",), ("HBs Ag (Screen Test)",), ("TPHA",), ("VDRL",),
        ("Group & Rh Factor",), ("Mantaux-Test (M.T)",), ("Triple Antigen",), ("R.Fever",), ("HIV",), ("HCV",),
        ("Random Blood Sugar (RBS)",), ("Fasting Blood Sugar (FBS)",), ("2hr. After Breakfast",),
        ("Blood Urea",), ("Cholesterol",), ("TG (Triglycerides)",), ("S.GPT (ALT)",), ("S.GOT (AST)",),
        ("Bilirubin Total",), ("Lipid Profile",), ("Serum Creatinine",), ("Uric Acid",),
        ("Urine Pregnancy Test (PT)",), ("Urine R/E",), ("Stool R/E",),
        ("USG Whole Abdomen",), ("USG Upper Abdomen",), ("USG Lower Abdomen",), ("USG KUB",), ("USG Pregnancy Profile",),
        ("X-Ray Chest",), ("X-Ray PNS",), ("X-Ray Cervical Spine",), ("X-Ray L/S Spine",), ("X-Ray Knee B/V",)
    ]
    c.executemany("INSERT INTO custom_tests_list (test_name) VALUES (?)", default_tests)
    conn.commit()

# 🌟 Retrieve the names of all tests saved so far from the database (auto-updated list)
c.execute("SELECT test_name FROM custom_tests_list")
available_tests = [row[0] for row in c.fetchall()]
available_tests.sort()

st.title("📝 টেস্ট এবং বিলিং সেকশন")

st.subheader("পেশেন্ট ইনফরমেশন")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("পেশেন্টের নাম (Name of the PT) *")
    phone = st.text_input("মোবাইল নম্বর (Phone)")
with col2:
    age = st.number_input("বয়স (Age)", min_value=1, max_value=120, value=25)
    
    # Retrieving all doctor names from the database
    c.execute("SELECT doc_name FROM doctors_list")
    db_doctors = [row[0] for row in c.fetchall()]
    
    doctor_options = db_doctors + ["অন্যান্য"]
    selected_doctor_setup = st.selectbox("ডাক্তার সিলেক্ট করুন (Refd By)", doctor_options)
    
    if selected_doctor_setup == "অন্যান্য":
        doctor = st.text_input("✍️ নতুন ডাক্তারের নাম ও ডিগ্রি এখানে লিখুন: *")
    else:
        doctor = selected_doctor_setup

st.markdown("---")
st.subheader("টেস্ট সিলেকশন ও লাইভ রেট এন্ট্রি")

# Now the dropdown will show the list of tests updated live from the database
selected_tests = st.multiselect("তালিকা থেকে টেস্ট সিলেক্ট করুন:", available_tests)

test_with_prices = []
total_fee = 0.0

if selected_tests:
    st.markdown("##### 💰 নির্বাচিত টেস্টগুলোর দাম এখানে হাতে লিখে দিন:")
    for test in selected_tests:
        price = st.number_input(f"রেট দিন -> {test} (টাকা):", min_value=0.0, step=50.0, key=f"price_{test}")
        total_fee += price
        test_with_prices.append(f"{test}:{price}")

# Custom test option (enter a new test name outside the list)
st.markdown("##### ➕ তালিকা বহির্ভূত কাস্টম টেস্ট (ঐচ্ছিক)")
col_c1, col_c2 = st.columns(2)
with col_c1:
    custom_name = st.text_input("কাস্টম টেস্টের নাম:")
with col_c2:
    custom_price = st.number_input("কাস্টম টেস্টের দাম:", min_value=0.0, step=50.0)

if custom_name.strip():
    total_fee += custom_price
    test_with_prices.append(f"{custom_name.strip()}:{custom_price}")

st.info(f"📋 লাইভ মোট বিল (টোটাল充 ফি): {total_fee} টাকা")
with col3:
    discount_amount = st.number_input("ডিসকাউন্ট (টাকা)", min_value=0.0, value=0.0, step=10.0)
    advance_paid = st.number_input("অগ্রিম পরিশোধ (Advance Paid)", min_value=0.0, value=0.0)

net_payable = total_fee - discount_amount
due_amount = net_payable - advance_paid

with col4:
    st.metric("ডিসকাউন্ট প্রদত্ত (টাকা)", f"{discount_amount} ৳")
    st.metric("মোট বাকি টাকা (Due)", f"{due_amount} ৳")
    
st.markdown("---")
submit_button = st.button("Save Bill and Go to Print (ডাটা সেভ করুন)")

if submit_button:
    if not name or not test_with_prices:
        st.error("⚠️ পেশেন্টের নাম এবং অন্তত একটি টেস্টের দাম দেওয়া বাধ্যতামূলক!")
    elif selected_doctor_setup == "অন্যান্য" and not doctor.strip():
        st.error("⚠️ দয়া করে নতুন ডাক্তারের নাম টেক্সট বক্সে লিখুন!")
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        tests_data_str = "|".join(test_with_prices)
        
        # 🌟 জাদুকরী লজিক ১: নতুন কোনো ডাক্তারের নাম ইনপুট দেওয়া হলে তা তালিকায় অটো-সেভ হবে
        if selected_doctor_setup == "অন্যান্য" and doctor.strip():
            try:
                c.execute("INSERT OR IGNORE INTO doctors_list (doc_name) VALUES (?)", (doctor.strip(),))
                conn.commit()
            except:
                pass
                
        # 🌟 জাদুকরী লজিক ২: নতুন কোনো কাস্টম টেস্টের নাম লিখলে তা তালিকায় আজীবনের জন্য অটো-সেভ হবে
        if custom_name.strip():
            try:
                c.execute("INSERT OR IGNORE INTO custom_tests_list (test_name) VALUES (?)", (custom_name.strip(),))
                conn.commit()
            except:
                pass
        
                c.execute("""
            INSERT INTO billing_records (patient_name, age, phone, doctor, selected_tests, total_amount, discount_percent, net_paid, due_amount, billing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, age, phone, doctor.strip() if hasattr(doctor, 'strip') else doctor, tests_data_str, total_fee, discount_amount, advance_paid, due_amount, current_date))
        conn.commit()
        st.session_state.last_invoice_id = c.lastrowid
        st.success("✅ সফলভাবে ডাটা সেভ হয়েছে! প্রিন্ট পেজে নিয়ে যাওয়া হচ্ছে...")
        st.switch_page("pages/3_Print_Receipt.py")

conn.close()
