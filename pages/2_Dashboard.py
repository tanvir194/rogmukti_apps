import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# 🔑 1. Admin Security Lock Code (at the very beginning)
ADMIN_PASSWORD = "12345"

if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    st.warning("🔒 এই পেজটি লক করা আছে। দেখার জন্য অ্যাডমিন পাসওয়ার্ড দিন।")
    password_box = st.text_input("🔑 পাসওয়ার্ড লিখুন:", type="password", key="lock_dashboard")
    
    if st.button("🔓 আনলক করুন", type="primary", key="btn_dashboard"):
        if password_box == ADMIN_PASSWORD:
            st.session_state.admin_auth = True
            st.success("🎉 সফলভাবে আনলক হয়েছে!")
            st.rerun()
        else:
            st.error("❌ ভুল পাসওয়ার্ড!")
    st.stop()

# 📊 2. Dashboard main accounting code
st.title("📊 দৈনিক ও মাসিক ক্যাশ হিসাব-নিকাশ")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rogmukti_clinic_fix.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 🌟 Magical logic: ensuring the table is created before the dashboard loads (error resolution)
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
    billing_date TEXT,
    ref_fee REAL DEFAULT 0.0
)
""")
conn.commit()

try:
    df = pd.read_sql_query("SELECT * FROM billing_records", conn)
    
    if not df.empty:
        df['billing_date'] = pd.to_datetime(df['billing_date'], errors='coerce')
        df = df.dropna(subset=['billing_date'])
        
        option = st.radio("কোন হিসাবটি দেখতে চান?", ["আজকের/দৈনিক হিসাব", "মাসিক হিসাব"], horizontal=True)
        
        if option == "আজকের/দৈনিক হিসাব":
            user_date = st.date_input("📅 নির্দিষ্ট তারিখ সিলেক্ট করুন:", datetime.now().date())
            filtered_df = df[df['billing_date'].dt.date == user_date]
        else:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                available_years = sorted(df['billing_date'].dt.year.unique())
                if datetime.now().year not in available_years:
                    available_years.append(datetime.now().year)
                selected_year = st.selectbox("বছর সিলেক্ট করুন:", available_years, index=available_years.index(datetime.now().year))
            
            with col_m2:
                months_bn = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                current_month = datetime.now().month
                selected_month = st.selectbox("মাস সিলেক্ট করুন:", range(1, 13), index=current_month-1, format_func=lambda x: months_bn[x-1])
            
            filtered_df = df[(df['billing_date'].dt.month == selected_month) & (df['billing_date'].dt.year == selected_year)]
        
        st.markdown("---")
        
        if not filtered_df.empty:
            st.success(f"📋 মোট {len(filtered_df)} টি বিলের তথ্য পাওয়া গেছে।")
            
            box1, box2, box3, box4 = st.columns(4)
            with box1:
                st.metric("💰 মোট বিল (Total)", f"{filtered_df['total_amount'].sum():,.2f} ৳")
            with box2:
                st.metric("✅ মোট নগদ আদায়", f"{filtered_df['net_paid'].sum():,.2f} ৳")
            with box3:
                st.metric("🚨 মোট বাকি টাকা (Due)", f"{filtered_df['due_amount'].sum():,.2f} ৳")
            with box4:
                total_ref = filtered_df['ref_fee'].sum() if 'ref_fee' in filtered_df.columns else 0.0
                st.metric("🩺 মোট ডাক্তার রেফার ফি", f"{total_ref:,.2f} ৳")
                
            st.subheader("🩺 ডাক্তারদের রেফারেন্স ফি-র হিসাব")
            if 'ref_fee' in filtered_df.columns and 'doctor' in filtered_df.columns:
                doc_fee_df = filtered_df.groupby('doctor')['ref_fee'].sum().reset_index()
                doc_fee_df = doc_fee_df.rename(columns={'doctor': 'ডাক্তারের নাম', 'ref_fee': 'মোট প্রদেয় রেফার ফি (টাকা)'})
                st.dataframe(doc_fee_df, use_container_width=True, hide_index=True)
            
            st.subheader("📋 বিলের বিস্তারিত তালিকা")
            display_df = filtered_df.copy()
            display_df['billing_date'] = display_df['billing_date'].dt.strftime('%Y-%m-%d')
            display_df['selected_tests'] = display_df['selected_tests'].str.replace('|', ', ', regex=False)
            
            display_df = display_df.rename(columns={
                'id': 'বিল নং', 'patient_name': 'রোগীর নাম', 'age': 'বয়স',
                'phone': 'মোবাইল', 'selected_tests': 'টেস্টসমূহ', 'doctor': 'রেফার করা ডাক্তার',
                'total_amount': 'মোট বিল', 'net_paid': 'ক্যাশ পেইড',
                'due_amount': 'বাকি (Due)', 'billing_date': 'তারিখ', 'ref_fee': 'রেফার ফি'
            })
            
            available_cols = ['বিল নং', 'তারিখ', 'রোগীর নাম', 'রেফার করা ডাক্তার', 'টেস্টসমূহ', 'মোট বিল', 'ক্যাশ পেইড', 'বাকি (Due)']
            if 'রেফার ফি' in display_df.columns:
                available_cols.append('রেফার ফি')
                
            st.dataframe(display_df[available_cols], use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ এই তারিখে বা মাসে কোনো বিল তৈরি করা হয়নি।")
    else:
        st.info("ℹ️ ডাটাবেজে এখনো কোনো রোগীর বিলের ডাটা সেভ করা হয়নি।")
except Exception as e:
    st.error(f"❌ ডাটাবেজ লোড হতে সমস্যা হচ্ছে। এরর বিবরণ: {e}")

conn.close()
