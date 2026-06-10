import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Pathology Report", layout="wide")

st.title("🧪 Pathology Reports")
st.markdown("**অটোমেটিক রিপোর্ট জেনারেটর সহ প্যাথলজি সিস্টেম**")

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

tab1, tab2 = st.tabs(["➕ নতুন অটো রিপোর্ট", "📋 সব রিপোর্ট"])

with tab1:
    st.subheader("অটোমেটিক রিপোর্ট জেনারেট করুন")

    # Patient Selection
    try:
        patients = pd.read_sql_query("SELECT DISTINCT patient_name, phone, doctor FROM billing_records ORDER BY billing_date DESC", conn)
        patient_list = ["নতুন রোগী"] + sorted(patients['patient_name'].unique().tolist())
        selected_patient = st.selectbox("রোগীর নাম সিলেক্ট করুন", patient_list)
        
        if selected_patient != "নতুন রোগী":
            row = patients[patients['patient_name'] == selected_patient].iloc[0]
            def_name = row['patient_name']
            def_phone = row.get('phone', '')
            def_doctor = row.get('doctor', '')
        else:
            def_name = def_phone = def_doctor = ""
    except:
        def_name = def_phone = def_doctor = ""

    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("রোগীর নাম *", value=def_name)
        patient_phone = st.text_input("মোবাইল", value=def_phone)
        test_name = st.text_input("টেস্টের নাম *")
    with col2:
        report_date = st.date_input("রিপোর্ট তারিখ", datetime.now().date())
        doctor_name = st.text_input("রেফার ডাক্তার", value=def_doctor)

    st.markdown("### টেস্ট রেজাল্ট দিন")
    result = st.text_area("রেজাল্ট লিখুন (যেমন: Blood Group: B Positive\nHBsAg: Negative\nRandom: 4.85 mmol/L)", height=200)

    notes = st.text_area("অতিরিক্ত নোট / মন্তব্য", height=100)

    uploaded_file = st.file_uploader("অতিরিক্ত ফাইল আপলোড (ঐচ্ছিক)", 
                                   type=["pdf", "png", "jpg", "jpeg", "doc", "docx"])

    if st.button("🖨️ রিপোর্ট জেনারেট ও সেভ করুন", type="primary", use_container_width=True):
        if patient_name and test_name and result:
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

            # Show Printable Report
            st.success("✅ রিপোর্ট সেভ হয়েছে!")
            
            st.markdown("---")
            st.subheader("🖨️ প্রিন্ট রেডি রিপোর্ট")
            
            st.markdown(f"""
            <div style="border: 2px solid #333; padding: 30px; margin: 20px 0; font-family: Arial;">
                <h2 style="text-align: center;">Pathology Report</h2>
                <p><strong>রোগীর নাম:</strong> {patient_name} &nbsp;&nbsp;&nbsp; <strong>মোবাইল:</strong> {patient_phone}</p>
                <p><strong>রেফার ডাক্তার:</strong> {doctor_name} &nbsp;&nbsp;&nbsp; <strong>তারিখ:</strong> {report_date}</p>
                <p><strong>পরীক্ষা:</strong> {test_name}</p>
                <hr>
                <pre style="font-size: 16px; white-space: pre-wrap;">{result}</pre>
                {f"<p><strong>নোট:</strong> {notes}</p>" if notes else ""}
            </div>
            """, unsafe_allow_html=True)

            st.info("↑ উপরের রিপোর্টটি সিলেক্ট করে **Ctrl + P** চাপুন প্রিন্ট করার জন্য")

        else:
            st.error("রোগীর নাম, টেস্টের নাম এবং রেজাল্ট দিতে হবে")

with tab2:
    st.subheader("সকল সেভকৃত রিপোর্ট")
    df = pd.read_sql_query("SELECT * FROM pathology_reports ORDER BY id DESC", conn)
    
    if not df.empty:
        for _, row in df.iterrows():
            with st.expander(f"{row['patient_name']} - {row['test_name']} ({row['report_date']})"):
                st.write(f"**ডাক্তার:** {row['doctor_name']}")
                st.text_area("রেজাল্ট", value=row['result'], height=200, disabled=True)
                if row['notes']:
                    st.write("**নোট:**", row['notes'])
                if row['file_path']:
                    file_path = os.path.join(UPLOAD_FOLDER, row['file_path'])
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            st.download_button("📥 ডাউনলোড", f, row['file_path'])
    else:
        st.info("এখনো কোনো রিপোর্ট নেই")

conn.close()
