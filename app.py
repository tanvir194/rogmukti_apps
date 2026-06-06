import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# পেজ কনফিগারেশন
st.set_page_config(
    page_title="রোগমুক্তি ক্লিনিক ম্যানেজমেন্ট সিস্টেম", 
    layout="wide"
)
# ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic.db", check_same_thread=False)
c = conn.cursor()

# টেবিল তৈরি (সঠিক কলামের নামসহ)
c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    phone TEXT,
    doctor TEXT,
    tests TEXT,
    total_amount REAL,
    discount REAL,
    advance REAL,
    due REAL,
    date TEXT
)
""")
conn.commit()

# ডাটাবেজে তথ্য সেভ করার ফাংশন
def add_patient(name, age, phone, doctor, tests, total, discount, advance, due, date):
    c.execute('''
        INSERT INTO patients (name, age, phone, doctor, tests, total_amount, discount, advance, due, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, phone, doctor, tests, total, discount, advance, due, date))
    conn.commit()
# মূল শিরোনাম
st.title("🏥 রোগমুক্তি ক্লিনিক ম্যানেজমেন্ট সিস্টেম")
st.markdown("---")

# সাইডবার নেভিগেশন মেনু
st.sidebar.title("🧭 নেভিগেশন মেনু")
page = st.sidebar.radio("অপশন সিলেক্ট করুন:", ["নতুন পেশেন্ট এন্ট্রি", "পেশেন্ট ডাটাবেজ"])
if page == "নতুন পেশেন্ট এন্ট্রি":
    st.subheader("👤 পেশেন্ট এবং ডাক্তারের তথ্য")
    
    with st.form("patient_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name of the PT (পেশেন্টের নাম) *")
            age = st.number_input("Age (বয়স)", min_value=0, max_value=120, value=25)
            phone = st.text_input("Phone (মোবাইল নম্বর)")
            
        with col2:
            # ডাক্তারদের একটি তালিকা (প্রয়োজনে নাম পরিবর্তন করতে পারেন)
            doctor_list = ["ডা. সাইদুল ইসলাম", "ডা. নাসরিন সুলতানা", "অন্যান্য"]
            doctor = st.selectbox("REFD BY. DR (ডাক্তার সিলেক্ট করুন)", doctor_list)
            
            date_input = st.date_input("Date (তারিখ)", datetime.now())
            date_str = date_input.strftime("%Y-%m-%d")
            
        st.markdown("---")
        st.subheader("🧪 টেস্ট এবং বিলিং")
        
        # মাল্টি-সিলেক্ট টেস্ট বক্স
        available_tests = ["CBC (Complete Blood Count)", "Hgb (Hemoglobin)", "WBC Count", "Platelet Count", "ETT", "USG of Thyroid Gland"]
        tests_selected = st.multiselect("Description (এখান থেকে সার্চ বা সিলেক্ট করুন)", available_tests)
        tests_str = ", ".join(tests_selected) # সিলেক্ট করা টেস্টগুলোকে টেক্সটে রূপান্তর
        
        # বিলিং সেকশন
        col3, col4 = st.columns(2)
        
        with col3:
            total_amount = st.number_input("সাব-টোটাল (Total Amount)", min_value=0.0, step=50.0, value=5250.0)
            discount = st.number_input("Discount (%)", min_value=0.0, step=1.0, value=20.0)
            advance = st.number_input("Advance (অগ্রিম পরিশোধ)", min_value=0.0, step=50.0, value=4200.0)
            
        with col4:
            # ডিসকাউন্ট এবং বাকি টাকা হিসাব করার লজিক
            discount_amount = total_amount * (discount / 100)
            due = total_amount - (discount_amount + advance)
            
            st.write("")
            st.write(f"**Total Amount:** {total_amount} টাকা")
            st.write(f"**Discount Given:** {discount_amount} টাকা")
            st.metric(label="Due (বাকি)", value=f"{due} টাকা")

        # সাবমিট বাটন
        submit_btn = st.form_submit_button("Save and Print Bill (ডাটা সেভ করুন)")
        
        if submit_btn:
            if name: # নাম দেওয়া বাধ্যতামূলক
                add_patient(name, age, phone, doctor, tests_str, total_amount, discount, advance, due, date_str)
                st.success(f"সফলভাবে {name}-এর তথ্য ডাটাবেজে সেভ হয়েছে!")
            else:
                st.error("অনুগ্রহ করে পেশেন্টের নাম লিখুন।")
elif page == "পেশেন্ট ডাটাবেজ":
    st.subheader("📋 সকল পেশেন্টের তালিকা")
    
    # ডাটাবেজ থেকে তথ্য আনা
    c.execute("SELECT * FROM patients ORDER BY id DESC")
    data = c.fetchall()
    
    if data:
        # টেবিলের হেডার সেট করা
        columns = ["ID", "নাম", "বয়স", "ফোন", "ডাক্তার", "টেস্টসমূহ", "মোট টাকা", "ছাড় (%)", "অগ্রিম", "বাকি", "তারিখ"]
        df = pd.DataFrame(data, columns=columns)
        
        # স্ক্রিনে প্রদর্শন
        st.dataframe(df, use_container_width=True)
    else:
        st.info("এখনো ডাটাবেজে কোনো পেশেন্টের তথ্য রেকর্ড করা হয়নি।")
