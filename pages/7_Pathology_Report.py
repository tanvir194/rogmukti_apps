import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Pathology Report", layout="wide")

st.title("🧪 Pathology Reports")
st.markdown("**সকল ধরনের প্যাথলজি ও ল্যাবরেটরি রিপোর্ট এখানে সেভ করা হবে**")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rogmukti_clinic_fix.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "pathology_reports")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create Pathology Table
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

# ================== MAIN TABS ==================
tab1, tab2 = st.tabs(["➕ নতুন রিপোর্ট যোগ করুন", "📋 সব রিপোর্ট দেখুন"])

with tab1:
    st.subheader("নতুন প্যাথলজি রিপোর্ট যোগ করুন")

    # Existing Patient Selection
    st.markdown("**আগের এন্ট্রি করা রোগী সিলেক্ট করুন**")
    patients = pd.read_sql_query("""
        SELECT DISTINCT patient_name, phone, doctor 
        FROM billing_records 
        ORDER BY billing_date DESC
    """, conn)
    
    if not patients.empty:
        patient_list = patients['patient_name'].unique().tolist()
        selected_patient = st.selectbox("রোগীর নাম সিলেক্ট করুন", ["নতুন রোগী"] + patient_list)
        
        if selected_patient != "নতুন রোগী":
            patient_data = patients[patients['patient_name'] == selected_patient].iloc[0]
            patient_name = patient_data['patient_name']
            patient_phone = patient_data['phone']
            doctor_name = patient_data['doctor']
        else:
            patient_name = ""
            patient_phone = ""
            doctor_name = ""
    else:
        selected_patient = "নতুন রোগী"
        patient_name = ""
        patient_phone = ""
        doctor_name = ""

    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("রোগীর নাম *", value=patient_name)
        patient_phone = st.text_input("মোবাইল নম্বর", value=patient_phone)
        test_name = st.text_input("টেস্টের নাম / পরীক্ষা *")
    
    with col2:
        report_date = st.date_input("রিপোর্টের তারিখ", datetime.now().date())
        doctor_name = st.text_input("রেফার করা ডাক্তার", value=doctor_name)

    result = st.text_area("রিপোর্ট / ফলাফল", height=150)
    notes = st.text_area("অতিরিক্ত নোট", height=100)

    uploaded_file = st.file_uploader("রিপোর্ট ফাইল আপলোড (PDF/Image)", 
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
                (patient_name, patient_phone, test_name, str(report_date), doctor_name, result, notes, file_path))
            conn.commit()
            st.success("✅ রিপোর্ট সফলভাবে সেভ হয়েছে!")
            st.rerun()
        else:
            st.error("রোগীর নাম এবং টেস্টের নাম দিতে হবে")

with tab2:
    st.subheader("সকল সেভকৃত রিপোর্ট")
    df = pd.read_sql_query("SELECT * FROM pathology_reports ORDER BY report_date DESC", conn)
    if not df.empty:
        search = st.text_input("🔍 সার্চ করুন (রোগী বা টেস্ট)")
        if search:
            df = df[df['patient_name'].str.contains(search, case=False, na=False) | 
                    df['test_name'].str.contains(search, case=False, na=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("এখনো কোনো রিপোর্ট সেভ করা হয়নি।")

conn.close()
