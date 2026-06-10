import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# 🔑 1. ADMIN SECURITY LOCK
ADMIN_PASSWORD = "12345"

if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    st.warning("🔒 This page is locked. Enter admin password to view.")
    password_box = st.text_input("🔑 Enter Password:", type="password", key="lock_dashboard")
    
    if st.button("🔓 Unlock Dashboard", type="primary", key="btn_dashboard"):
        if password_box == ADMIN_PASSWORD:
            st.session_state.admin_auth = True
            st.success("🎉 Successfully Unlocked!")
            st.rerun()
        else:
            st.error("❌ Incorrect Password!")
    st.stop()

# 📊 2. MAIN DASHBOARD
st.title("📊 Daily & Monthly Cash Accounting")

# Database Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rogmukti_clinic_fix.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Ensure table exists
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
        
        option = st.radio("What do you want to view?", 
                         ["Daily Accounting", "Monthly Accounting"], 
                         horizontal=True)
        
        if option == "Daily Accounting":
            user_date = st.date_input("📅 Select Date:", datetime.now().date())
            filtered_df = df[df['billing_date'].dt.date == user_date]
            
        else:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                available_years = sorted(df['billing_date'].dt.year.unique())
                if datetime.now().year not in available_years:
                    available_years.append(datetime.now().year)
                selected_year = st.selectbox("Select Year:", 
                                           available_years, 
                                           index=available_years.index(datetime.now().year))
            
            with col_m2:
                months_en = ["January", "February", "March", "April", "May", "June", 
                            "July", "August", "September", "October", "November", "December"]
                current_month = datetime.now().month
                selected_month = st.selectbox("Select Month:", 
                                            range(1, 13), 
                                            index=current_month-1, 
                                            format_func=lambda x: months_en[x-1])
            
            filtered_df = df[(df['billing_date'].dt.month == selected_month) & 
                           (df['billing_date'].dt.year == selected_year)]
        
        st.markdown("---")
        
        if not filtered_df.empty:
            st.success(f"📋 Total {len(filtered_df)} bills found.")
            
            box1, box2, box3, box4 = st.columns(4)
            with box1:
                st.metric("💰 Total Billed Amount", f"{filtered_df['total_amount'].sum():,.2f} ৳")
            with box2:
                st.metric("✅ Total Cash Collected", f"{filtered_df['net_paid'].sum():,.2f} ৳")
            with box3:
                st.metric("🚨 Total Due Amount", f"{filtered_df['due_amount'].sum():,.2f} ৳")
            with box4:
                total_ref = filtered_df['ref_fee'].sum() if 'ref_fee' in filtered_df.columns else 0.0
                st.metric("🩺 Total Doctor Referral Fee", f"{total_ref:,.2f} ৳")
                
            st.subheader("🩺 Doctor-wise Referral Fee Summary")
            if 'ref_fee' in filtered_df.columns and 'doctor' in filtered_df.columns:
                doc_fee_df = filtered_df.groupby('doctor')['ref_fee'].sum().reset_index()
                doc_fee_df = doc_fee_df.rename(columns={
                    'doctor': 'Doctor Name', 
                    'ref_fee': 'Total Referral Fee (৳)'
                })
                st.dataframe(doc_fee_df, use_container_width=True, hide_index=True)
            
            st.subheader("📋 Detailed Bill List")
            display_df = filtered_df.copy()
            display_df['billing_date'] = display_df['billing_date'].dt.strftime('%Y-%m-%d')
            display_df['selected_tests'] = display_df['selected_tests'].str.replace('|', ', ', regex=False)
            
            display_df = display_df.rename(columns={
                'id': 'Bill No',
                'patient_name': 'Patient Name',
                'age': 'Age',
                'phone': 'Phone',
                'selected_tests': 'Tests',
                'doctor': 'Referred Doctor',
                'total_amount': 'Total Amount',
                'net_paid': 'Cash Paid',
                'due_amount': 'Due Amount',
                'billing_date': 'Date',
                'ref_fee': 'Referral Fee'
            })
            
            available_cols = ['Bill No', 'Date', 'Patient Name', 'Referred Doctor', 
                            'Tests', 'Total Amount', 'Cash Paid', 'Due Amount']
            if 'Referral Fee' in display_df.columns:
                available_cols.append('Referral Fee')
                
            st.dataframe(display_df[available_cols], use_container_width=True, hide_index=True)
            
        else:
            st.warning("⚠️ No bills found for the selected date/month.")
    else:
        st.info("ℹ️ No billing data available in the database yet.")

except Exception as e:
    st.error(f"❌ Error loading database. Details: {e}")

conn.close()
