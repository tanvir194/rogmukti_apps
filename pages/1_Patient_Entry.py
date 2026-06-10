import streamlit as st
import sqlite3
from datetime import datetime

# সিকিউরিটি চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# ডাটাবেজ টেবিল
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

# টেস্টের নামের তালিকা (শুধু নাম, দাম এখানে লাগবে না কারণ আপনি নিজেই টাইপ করবেন)
available_tests = [
    "(CBC), ESR", "TC.DC", "HB%", "ESR", "Platelet Count", "MP", "BT/CT", "C/E Count",
    "Widal", "Aso Titre", "CRP", "RA/RF", "HBs Ag (Screen Test)", "TPHA", "VDRL",
    "Group & Rh Factor", "Mantaux-Test (M.T)", "Triple Antigen", "R.Fever", "HIV", "HCV",
    "Random Blood Sugar (RBS)", "Fasting Blood Sugar (FBS)", "2hr. After Breakfast",
    "Blood Urea", "Cholesterol", "TG (Triglycerides)", "S.GPT (ALT)", "S.GOT (AST)",
    "Bilirubin Total", "Lipid Profile", "Serum Creatinine", "Uric Acid",
    "Urine Pregnancy Test (PT)", "Urine R/E", "Stool R/E",
    "USG Whole Abdomen", "USG Upper Abdomen", "USG Lower Abdomen", "USG KUB", "USG Pregnancy Profile",
    "X-Ray Chest", "X-Ray PNS", "X-Ray Cervical Spine", "X-Ray L/S Spine", "X-Ray Knee B/V"
]
available_tests.sort()

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
st.subheader("টেস্ট সিলেকশন ও লাইভ রেট এন্ট্রি")

# ড্রপডাউন থেকে টেস্ট সিলেক্ট
selected_tests = st.multiselect("তালিকা থেকে টেস্ট সিলেক্ট করুন:", available_tests)

# 📌 💥 জাদুকরী লজিক: প্রতিটি সিলেক্ট করা টেস্টের জন্য স্ক্রিনে লাইভ প্রাইস ইনপুট বক্স তৈরি 💥
test_with_prices = []
total_fee = 0.0

if selected_tests:
    st.markdown("##### 💰 নির্বাচিত টেস্টগুলোর দাম এখানে হাত লিখে দিন:")
    for test in selected_tests:
        # স্ক্রিনে প্রতিটা টেস্টের পাশে দাম লেখার বক্স আসবে
        price = st.number_input(f"রেট দিন -> {test} (টাকা):", min_value=0.0, step=50.0, key=f"price_{test}")
        total_fee += price
        if price > 0:
            test_with_prices.append(f"{test}:{price}")
        else:
            test_with_prices.append(f"{test}:0")

# কাস্টম টেস্ট অপশন (তালিকার বাইরে কিছু থাকলে)
st.markdown("##### ➕ তালিকা বহির্ভূত কাস্টম টেস্ট (ঐচ্ছিক)")
col_c1, col_c2 = st.columns(2)
with col_c1:
    custom_name = st.text_input("কাস্টম টেস্টের নাম:")
with col_c2:
    custom_price = st.number_input("কাস্টম টেস্টের দাম:", min_value=0.0, step=50.0)

if custom_name.strip():
    total_fee += custom_price
    test_with_prices.append(f"{custom_name.strip()}:{custom_price}")

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
    if not name or not test_with_prices:
        st.error("⚠️ পেশেন্টের নাম এবং অন্তত একটি টেস্টের দাম দেওয়া বাধ্যতামূলক!")
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        # টেস্টের নাম ও দাম একসাথে জোড়া দিয়ে ডাটাবেজে পাঠানো হচ্ছে (যেমন: CBC:400, ESR:200)
        tests_data_str = "|".join(test_with_prices)
        
        c.execute("""
            INSERT INTO billing_records (patient_name, age, phone, doctor, selected_tests, total_amount, discount_percent, net_paid, due_amount, billing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, age, phone, doctor, tests_data_str, total_fee, discount_pct, advance_paid, due_amount, current_date))
        conn.commit()
        
        st.session_state.last_invoice_id = c.lastrowid
        st.success("✅ সফলভাবে ডাটা সেভ হয়েছে! প্রিন্ট পেজে নিয়ে যাওয়া হচ্ছে...")
        st.switch_page("pages/3_Print_Receipt.py")

conn.close()
