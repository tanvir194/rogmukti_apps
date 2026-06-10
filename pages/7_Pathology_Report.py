import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="AI Pathology Report", layout="wide")

st.title("🧠 AI Pathology Report Generator")
st.markdown("**Print Receipt থেকে রোগীর তথ্য অটো চলে আসবে**")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rogmukti_clinic_fix.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "pathology_reports")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS pathology_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT, 
    patient_phone TEXT, 
    test_name TEXT,
    report_date TEXT, 
    doctor_name TEXT, 
    result TEXT,
    notes TEXT, 
    file_path TEXT, 
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

tab1, tab2 = st.tabs(["🧠 নতুন AI রিপোর্ট", "📋 সব রিপোর্ট"])

with tab1:
    st.subheader("রোগী সিলেক্ট করুন (Receipt থেকে অটো লোড)")

    # Load recent patients from billing_records
    billing_df = pd.read_sql_query("""
        SELECT 
            patient_name, 
            phone, 
            doctor, 
            selected_tests,
            age,
            billing_date
        FROM billing_records 
        ORDER BY billing_date DESC, id DESC 
        LIMIT 30
    """, conn)

    if not billing_df.empty:
        # Patient Selection
        patient_list = sorted(billing_df['patient_name'].unique().tolist())
        selected_patient = st.selectbox("রোগীর নাম সিলেক্ট করুন", patient_list)

        # Get latest record of this patient
        patient_data = billing_df[billing_df['patient_name'] == selected_patient].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("রোগীর নাম *", value=patient_data['patient_name'])
            patient_phone = st.text_input("মোবাইল নম্বর", value=patient_data.get('phone', ''))
            age = st.text_input("বয়স", value=patient_data.get('age', ''))
        with col2:
            doctor_name = st.text_input("রেফার ডাক্তার", value=patient_data.get('doctor', ''))
            report_date = st.date_input("রিপোর্টের তারিখ", datetime.now().date())

        # Tests from Receipt
        tests = str(patient_data['selected_tests']).split('|') if pd.notna(patient_data['selected_tests']) else []
        st.info(f"**রিসিপ্ট থেকে পাওয়া টেস্ট:** {', '.join(tests)}")

        test_name = st.selectbox("কোন টেস্টের রিপোর্ট দিতে চান?", tests if tests else ["General Test"])

        st.markdown("### রেজাল্ট দিন")
        result = st.text_area("রেজাল্ট লিখুন", height=200, 
                            placeholder="এখানে রেজাল্ট লিখুন...")

        notes = st.text_area("অতিরিক্ত নোট / মন্তব্য", height=80)

        if st.button("🖨️ রিপোর্ট জেনারেট করে প্রিন্ট রেডি করুন", type="primary", use_container_width=True):
            if patient_name and test_name and result:
                c.execute("""INSERT INTO pathology_reports 
                    (patient_name, patient_phone, test_name, report_date, doctor_name, result, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (patient_name, patient_phone, test_name, str(report_date), 
                     doctor_name, result, notes))
                conn.commit()
                
                st.success("✅ রিপোর্ট সেভ হয়েছে!")

                # Beautiful Printable Report
                st.markdown("---")
                st.subheader("🖨️ প্রিন্ট রেডি রিপোর্ট")
                
                st.markdown(f"""
                <div style="border: 3px solid #1976D2; padding: 30px; border-radius: 15px; background-color: #f8fbff; margin: 10px 0;">
                    <h2 style="text-align: center; color: #1976D2;">ROGMUKTI DIAGNOSTIC CENTRE</h2>
                    <p style="text-align: center;">Mollah stand, Auliapur, Patuakhali</p>
                    <hr>
                    <p><strong>রোগীর নাম :</strong> {patient_name} &nbsp;&nbsp; <strong>বয়স :</strong> {age}</p>
                    <p><strong>মোবাইল :</strong> {patient_phone} &nbsp;&nbsp; <strong>তারিখ :</strong> {report_date}</p>
                    <p><strong>রেফার ডাক্তার :</strong> {doctor_name}</p>
                    <p><strong>পরীক্ষা :</strong> {test_name}</p>
                    <hr>
                    <pre style="font-size: 16px; background: #f0f4ff; padding: 15px; border-radius: 8px;">{result}</pre>
                    {f"<p><strong>নোট:</strong> {notes}</p>" if notes else ""}
                </div>
                """, unsafe_allow_html=True)

                st.info("**প্রিন্ট করার জন্য** ↑ উপরের অংশ সিলেক্ট করে **Ctrl + P** চাপুন")
            else:
                st.error("রেজাল্ট লিখুন")
    else:
        st.warning("এখনো কোনো রিসিপ্ট পাওয়া যায়নি। প্রথমে Receipt কাটুন।")

with tab2:
    st.subheader("সকল সেভকৃত রিপোর্ট")
    df = pd.read_sql_query("SELECT * FROM pathology_reports ORDER BY id DESC", conn)
    if not df.empty:
        for _, row in df.iterrows():
            with st.expander(f"{row['patient_name']} - {row['test_name']}"):
                st.write(f"**তারিখ:** {row['report_date']}")
                st.text_area("রেজাল্ট", row['result'], height=180, disabled=True)
                if row.get('notes'):
                    st.write("**নোট:**", row['notes'])
    else:
        st.info("এখনো কোনো রিপোর্ট সেভ হয়নি।")

conn.close()
