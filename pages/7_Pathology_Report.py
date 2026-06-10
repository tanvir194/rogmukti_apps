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

    # Auto patient fill
    try:
        patients_df = pd.read_sql_query("SELECT DISTINCT patient_name, phone, doctor FROM billing_records ORDER BY billing_date DESC LIMIT 100", conn)
        if not patients_df.empty:
            options = ["নতুন রোগী"] + sorted(patients_df['patient_name'].unique().tolist())
            selected = st.selectbox("রোগীর নাম সিলেক্ট করুন", options)
            if selected != "নতুন রোগী":
                row = patients_df[patients_df['patient_name'] == selected].iloc[0]
                def_name = row['patient_name']
                def_phone = row.get('phone', '')
                def_doctor = row.get('doctor', '')
            else:
                def_name = def_phone = def_doctor = ""
        else:
            def_name = def_phone = def_doctor = ""
    except:
        def_name = def_phone = def_doctor = ""

    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("রোগীর নাম *", value=def_name)
        patient_phone = st.text_input("মোবাইল নম্বর", value=def_phone)
        test_name = st.text_input("টেস্টের নাম / পরীক্ষা *")
    with col2:
        report_date = st.date_input("রিপোর্টের তারিখ", datetime.now().date())
        doctor_name = st.text_input("রেফার করা ডাক্তার", value=def_doctor)

    result = st.text_area("রিপোর্ট / ফলাফল", height=150)
    notes = st.text_area("অতিরিক্ত নোট", height=100)

    uploaded_file = st.file_uploader("রিপোর্ট ফাইল আপলোড করুন", 
                                   type=["pdf", "png", "jpg", "jpeg", "doc", "docx"],
                                   help="PDF, DOC, DOCX, JPG, PNG সমর্থিত")

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
            st.success("✅ রিপোর্ট সেভ হয়েছে!")
            st.rerun()
        else:
            st.error("রোগীর নাম এবং টেস্টের নাম দিতে হবে")

with tab2:
    st.subheader("সকল সেভকৃত রিপোর্ট")
    df = pd.read_sql_query("SELECT * FROM pathology_reports ORDER BY report_date DESC", conn)
    
    if not df.empty:
        search = st.text_input("🔍 সার্চ (রোগী/টেস্ট)")
        if search:
            df = df[df['patient_name'].str.contains(search, case=False, na=False) | 
                    df['test_name'].str.contains(search, case=False, na=False)]
        
        for index, row in df.iterrows():
            col_a, col_b, col_c = st.columns([3, 2, 2])
            with col_a:
                st.write(f"**{row['patient_name']}** - {row['test_name']} ({row['report_date']})")
            with col_b:
                if row['file_path']:
                    file_full_path = os.path.join(UPLOAD_FOLDER, row['file_path'])
                    if os.path.exists(file_full_path):
                        with open(file_full_path, "rb") as f:
                            st.download_button("📥 ডাউনলোড", f, file_name=row['file_path'], key=f"dl_{row['id']}")
            with col_c:
                st.write(" ")
            st.divider()
    else:
        st.info("এখনো কোনো রিপোর্ট সেভ করা হয়নি।")

conn.close()
