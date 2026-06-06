import streamlit as st
import sqlite3
from datetime import datetime

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="রোগমুক্তি ক্লিনিক ম্যানেজমেন্ট", page_icon="🏥", layout="wide")

# ২. ডাটাবেজ সেটআপ
conn = sqlite3.connect("rogmukti_clinic.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    phone TEXT,
    doctor TEXT,
    tests TEXT,
    total_amount REAL,
    date TEXT
)
""")
conn.commit()

# ৩. ডাক্তার ও টেস্টের তালিকা
doctors_list = ["সিলেক্ট করুন", "ডা. সাইফুল ইসলাম", "ডা. এ. রহমান", "ডা. সুফিয়া খাতুন"]
available_tests = {
    "CBC (রক্ত পরীক্ষা)": 400,
    "X-Ray Chest": 500,
    "Ultrasonography": 1200,
    "Urine R/E": 250,
    "Blood Sugar": 150
}

# ৪. সাইডবার মেনু
st.sidebar.header("🏥 নেভিগেশন মেনু")
menu = st.sidebar.radio("অপশন সিলেক্ট করুন:", ["নতুন পেশেন্ট এন্ট্রি", "বিলিং ও রিসিট", "পেশেন্ট ডাটাবেজ"])

st.title("🏥 রোগমুক্তি ক্লিনিক ম্যানেজমেন্ট সিস্টেম")
st.write("---")

# ৫. নতুন পেশেন্ট এন্ট্রি
if menu == "নতুন পেশেন্ট এন্ট্রি":
    st.subheader("👤 পেশেন্ট এবং ডাক্তারের তথ্য")
    
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("পেশেন্টের নাম")
        age = st.number_input("পেশেন্টের বয়স", min_value=1, max_value=120, value=25)
        phone = st.text_input("মোবাইল নম্বর")
    
    with col2:
        doctor = st.selectbox("রেফার্ড ডাক্তার (Referred By)", doctors_list)
        date_today = st.date_input("তারিখ", datetime.now())

    st.write("---")
    st.subheader("🧪 টেস্ট এবং বিলিং")
    
    selected_tests = st.multiselect("প্রয়োজনীয় টেস্টগুলো সিলেক্ট করুন", list(available_tests.keys()))
    
    # মোট বিল হিসাব
    total_amount = sum(available_tests[test] for test in selected_tests)
    st.markdown(f"### 💰 মোট বিল: **{total_amount} টাকা**")
    
    if st.button("ডাটা সেভ করুন এবং বিল তৈরি করুন"):
        if patient_name and phone and doctor != "সিলেক্ট করুন" and selected_tests:
            tests_str = ", ".join(selected_tests)
            c.execute("""
                INSERT INTO patients (name, age, phone, doctor, tests, total_amount, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (patient_name, age, phone, doctor, tests_str, total_amount, str(date_today)))
            conn.commit()
            st.success(f"✅ {patient_name} এর তথ্য সফলভাবে ডাটাবেজে সেভ হয়েছে!")
        else:
            st.error("⚠️ দয়া করে সব তথ্য সঠিকভাবে পূরণ করুন এবং অন্তত একটি টেস্ট সিলেক্ট করুন।")

# ৬. বিলিং ও রিসিট সেকশন
elif menu == "বিলিং ও রিসিট":
    st.subheader("🧾 পেশেন্ট রিসিট ও ইনভয়েস প্রিন্ট")
    phone_search = st.text_input("পেশেন্টের মোবাইল নম্বর দিয়ে খুঁজুন")
    
    if phone_search:
        c.execute("SELECT * FROM patients WHERE phone = ? ORDER BY id DESC", (phone_search,))
        patient = c.fetchone()
        
        if patient:
            st.markdown(f"""
            ### **মানি রিসিট (রোগমুক্তি ডায়াগনস্টিক)**
            - **ইনভয়েস আইডি:** #{patient[0]}
            - **পেশেন্টের নাম:** {patient[1]}  |  **বয়স:** {patient[2]}
            - **মোবাইল নম্বর:** {patient[3]}
            - **ডাক্তার:** {patient[4]}
            - **তারিখ:** {patient[7]}
            ---
            - **টেস্টের তালিকা:** {patient[5]}
            ### **মোট পরিশোধযোগ্য বিল: {patient[6]} টাকা**
            """)
            st.button("প্রিন্ট করুন (Ctrl + P)")
        else:
            st.warning("🔍 এই নম্বরে কোনো পেশেন্ট পাওয়া যায়নি।")

# ৭. পেশেন্ট ডাটাবেজ
elif menu == "পেশেন্ট ডাটাবেজ":
    st.subheader("📊 নিবন্ধিত পেশেন্টদের তালিকা")
    c.execute("SELECT id, name, age, phone, doctor, total_amount, date FROM patients ORDER BY id DESC")
    data = c.fetchall()
    
    if data:
        # সুন্দর টেবিল আকারে দেখানোর জন্য ডাটা ফরম্যাট করা
        st.table([
            {"আইডি": row[0], "নাম": row[1], "বয়স": row[2], "মোবাইল": row[3], "ডাক্তার": row[4], "মোট বিল (টাকা)": row[5], "তারিখ": row[6]}
            for row in data
        ])
    else:
        st.info("এখনো কোনো পেশেন্টের তথ্য এন্ট্রি করা হয়নি।")

conn.close()

