import sys
import os
sys.path.append(os.path.dirname(__file__))
from sidebar_monitor import show_live_sidebar
show_live_sidebar()

import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# 🔑 1. Admin Security Lock Code (At the very beginning)
ADMIN_PASSWORD = "12345"

if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    st.warning("🔒 This page is locked. Please enter the admin password to view.")
    password_box = st.text_input("🔑 Enter Password:", type="password", key="lock_dr_ref")
    
    if st.button("🔓 Unlock", type="primary", key="btn_dr_ref"):
        if password_box == ADMIN_PASSWORD:
            st.session_state.admin_auth = True
            st.success("🎉 Successfully unlocked!")
            st.rerun()
        else:
            st.error("❌ Incorrect password!")
    st.stop()

# 🩺 2. Doctor Referral Fee Main Code
st.title("🩺 Doctor Referral Fee & Commission Calculator")
st.write("---")

# Directory path fixed
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rogmukti_clinic_fix.db")

conn = sqlite3.connect(DB_PATH)

try:
    # Reading billing records from database
    df = pd.read_sql_query("SELECT id, patient_name, doctor, total_amount, billing_date FROM billing_records", conn)
    
    if not df.empty:
        df['billing_date'] = pd.to_datetime(df['billing_date'], errors='coerce')
        df = df.dropna(subset=['billing_date'])
        
        st.subheader("🔍 Filters & Calculation Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            doctor_list = sorted(df['doctor'].unique().tolist())
            selected_doctor = st.selectbox("🩺 Select Doctor:", doctor_list)
        
        with col2:
            today = datetime.now().date()
            start_date = st.date_input("📅 Start Date:", datetime(today.year, today.month, 1).date())
            end_date = st.date_input("📅 End Date:", today)
            
        if start_date > end_date:
            st.error("⚠️ Start date must be less than or equal to the end date!")
            st.stop()
            
        filtered_df = df[
            (df['doctor'] == selected_doctor) & 
            (df['billing_date'].dt.date >= start_date) & 
            (df['billing_date'].dt.date <= end_date)
        ]
        
        st.markdown("---")
        st.subheader("💰 Commission Percentage (%) Entry")
        
        total_business = filtered_df['total_amount'].sum() if not filtered_df.empty else 0.0
        
        box1, box2 = st.columns(2)
        with box1:
            st.info(f"📊 Total bill amount for **{selected_doctor}** in the selected period: **{total_business:,.2f} BDT**")
            commission_pct = st.number_input("🔗 How much percent (%) commission do you want to give?:", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
        
        calculated_commission = (total_business * commission_pct) / 100.0
        
        with box2:
            st.metric(label=f"🎯 Auto Payable Referral Fee ({commission_pct}%)", value=f"{calculated_commission:,.2f} BDT")
            st.caption(f"Total calculation from {start_date} to {end_date}")

        st.markdown("---")
        st.subheader(f"📋 Patient Details List for {selected_doctor}")
        if not filtered_df.empty:
            st.success(f"📈 Total {len(filtered_df)} billing records found for this period.")
            
            display_df = filtered_df.copy()
            display_df['billing_date'] = display_df['billing_date'].dt.strftime('%Y-%m-%d')
            display_df = display_df.rename(columns={
                'id': 'Bill No', 'patient_name': 'Patient Name', 
                'total_amount': 'Total Bill (BDT)', 'billing_date': 'Date'
            })
            
            st.dataframe(display_df[['Bill No', 'Date', 'Patient Name', 'Total Bill (BDT)']], use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ No patient bills found for this doctor within the selected date range.")
            
    else:
        st.info("ℹ️ No patient billing data saved in the database yet.")
except Exception as e:
    st.error(f"❌ Error loading data. Error details: {e}")

conn.close()
