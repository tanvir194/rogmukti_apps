import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Pathology Report", layout="wide")

st.title("🧪 Pathology Reports")
st.markdown("**সকল ধরনের প্যাথলজি ও ল্যাবরেটরি রিপোর্ট এখানে সেভ করা হবে**")

# Database Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rogmukti_clinic_fix.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "pathology_reports")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create Table (এখানে জোর করে টেবিল তৈরি করা হচ্ছে)
c.execute("""
CREATE TABLE IF NOT EXISTS pathology_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    patient_phone TEXT,
    test_name TEXT NOT NULL,
    report_date TEXT NOT NULL,
    doctor_name TEXT,
    result TEXT,
    notes TEXT,
    file_path TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

tab1, tab2 = st.tabs(["➕ নতুন রিপোর্ট যোগ করুন", "📋 সব রিপোর্ট দেখুন"])

with tab1:
    st.subheader("নতুন প্যাথলজি রিপোর্ট যোগ করুন")
    col1, col2 = st.columns(2)
    
    with col1:
        patient_name = st.text_input("রোগীর নাম *")
        patient_phone = st.text_input("মোবাইল নম্বর")
        test_name = st.text_input("টেস্টের নাম / পরীক্ষা *")
    
    with col2:
        report_date = st.date_input("রিপোর্টের তারিখ", datetime.now().date())
        doctor_name = st.text_input("রেফার করা ডাক্তার")
    
    result = st.text_area("রিপোর্ট / ফলাফল", height=150)
    notes = st.text_area("অতিরিক্ত নোট / মন্তব্য", height=100)
    
    uploaded_file = st.file_uploader("রিপোর্ট ফাইল আপলোড করুন (PDF বা ছবি)", 
                                   type=["pdf", "png", "jpg", "jpeg"])

    if st.button("💾 রিপোর্ট সেভ করুন", type="primary", use_container_width=True):
        if patient_name and test_name:
            file_path = None
            if uploaded_file:
                filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_path = filename

            c.execute("""INSERT INTO pathology_reports 
                (patient_name, patient_phone, test_name, report_date, doctor_name, result, notes, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (patient_name, patient_phone, test_name, str(report_date), 
                 doctor_name, result, notes, file_path))
            conn.commit()
            st.success("✅ রিপোর্ট সফলভাবে সেভ হয়েছে!")
            st.rerun()
        else:
            st.error("রোগীর নাম এবং টেস্টের নাম দিতে হবে")

with tab2:
    st.subheader("সকল সেভকৃত রিপোর্ট")
    try:
        df = pd.read_sql_query("""
            SELECT id, patient_name, patient_phone, test_name, 
                   report_date, doctor_name, result, notes 
            FROM pathology_reports 
            ORDER BY report_date DESC, id DESC
        """, conn)
        
        if not df.empty:
            search = st.text_input("🔍 রোগী বা টেস্ট দিয়ে সার্চ করুন")
            if search:
                df = df[df['patient_name'].str.contains(search, case=False, na=False) | 
                        df['test_name'].str.contains(search, case=False, na=False)]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("এখনো কোনো রিপোর্ট সেভ করা হয়নি।")
    except Exception as e:
        st.error(f"ডাটাবেসে সমস্যা: {e}")

conn.close()
