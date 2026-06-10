import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="AI Pathology Report", layout="wide")

st.title("🧠 AI Pathology Report Generator")
st.markdown("**Print Receipt থেকে অটো তথ্য নিয়ে আসা হয়েছে**")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rogmukti_clinic_fix.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "pathology_reports")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS pathology_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT, patient_phone TEXT, test_name TEXT,
    report_date TEXT, doctor_name TEXT, result TEXT,
    notes TEXT, file_path TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

tab1, tab2 = st.tabs(["🧠 নতুন AI রিপোর্ট", "📋 সব রিপোর্ট"])

with tab1:
    st.subheader("রোগী সিলেক্ট করুন")

    billing_df = pd.read_sql_query("""
        SELECT patient_name, phone, doctor, selected_tests, age, billing_date 
        FROM billing_records 
        ORDER BY billing_date DESC LIMIT 30
    """, conn)

    if not billing_df.empty:
        patient_list = sorted(billing_df['patient_name'].unique().tolist())
        selected_patient = st.selectbox("রোগীর নাম সিলেক্ট করুন", patient_list)

        patient_data = billing_df[billing_df['patient_name'] == selected_patient].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("রোগীর নাম *", value=patient_data['patient_name'])
            patient_phone = st.text_input("মোবাইল", value=patient_data.get('phone', ''))
        with col2:
            doctor_name = st.text_input("রেফার ডাক্তার", value=patient_data.get('doctor', ''))
            report_date = st.date_input("রিপোর্ট তারিখ", datetime.now().date())

        tests = str(patient_data['selected_tests']).split('|') if pd.notna(patient_data['selected_tests']) else []
        test_name = st.selectbox("টেস্ট সিলেক্ট করুন", tests if tests else ["General Test"])

        st.markdown("### রেজাল্ট লিখুন")
        result = st.text_area("রেজাল্ট", height=180, placeholder="এখানে রেজাল্ট লিখুন...")

        notes = st.text_area("নোট / মন্তব্য", height=80)

        if st.button("🖨️ প্রিন্ট রেডি রিপোর্ট জেনারেট করুন", type="primary", use_container_width=True):
            if result.strip():
                c.execute("""INSERT INTO pathology_reports 
                    (patient_name, patient_phone, test_name, report_date, doctor_name, result, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (patient_name, patient_phone, test_name, str(report_date), doctor_name, result, notes))
                conn.commit()

                st.success("✅ রিপোর্ট সেভ হয়েছে!")

                # ==================== IMPROVED PROFESSIONAL TEMPLATE ====================
                st.markdown("---")
                st.subheader("🖨️ প্রিন্ট রেডি প্রফেশনাল রিপোর্ট")

                html_report = f"""
                <div style="max-width: 800px; margin: 0 auto; padding: 30px; border: 2px solid #1e3a8a; font-family: Arial, sans-serif;">
                    <div style="text-align: center; border-bottom: 3px solid #1e3a8a; padding-bottom: 15px;">
                        <h1 style="color: #1e3a8a; margin: 0;">ROGMUKTI DIAGNOSTIC CENTRE</h1>
                        <p style="margin: 5px 0;">Mollah Stand, Auliapur, Patuakhali</p>
                        <p style="margin: 5px 0;">📞 01711867637</p>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; margin: 20px 0;">
                        <div>
                            <strong>রোগীর নাম :</strong> {patient_name}<br>
                            <strong>মোবাইল :</strong> {patient_phone}
                        </div>
                        <div style="text-align: right;">
                            <strong>তারিখ :</strong> {report_date}<br>
                            <strong>রেফার ডাক্তার :</strong> {doctor_name}
                        </div>
                    </div>

                    <div style="background: #f0f4ff; padding: 15px; border-radius: 8px; margin: 15px 0;">
                        <strong>পরীক্ষা :</strong> {test_name}
                    </div>

                    <div style="margin: 25px 0;">
                        <h3 style="color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 8px;">রিপোর্ট / ফলাফল</h3>
                        <pre style="font-size: 16px; line-height: 1.8; white-space: pre-wrap; background: white; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">{result}</pre>
                    </div>

                    {f"<div style='margin-top: 20px;'><strong>মন্তব্য :</strong> {notes}</div>" if notes else ""}
                    
                    <div style="margin-top: 40px; text-align: right; color: #444;">
                        <p>Dr. Farjana Rashid Shammy</p>
                        <p><small>Pathologist</small></p>
                    </div>
                </div>
                """

                st.markdown(html_report, unsafe_allow_html=True)
                st.info("**প্রিন্ট করার জন্য** ↑ উপরের রিপোর্ট সিলেক্ট করে **Ctrl + P** চাপুন")

with tab2:
    st.subheader("সকল সেভকৃত রিপোর্ট")
    df = pd.read_sql_query("SELECT * FROM pathology_reports ORDER BY id DESC", conn)
    if not df.empty:
        for _, row in df.iterrows():
            with st.expander(f"{row['patient_name']} - {row['test_name']}"):
                st.text_area("রেজাল্ট", row['result'], height=150, disabled=True)
                if row.get('notes'):
                    st.write("**নোট:**", row['notes'])
    else:
        st.info("এখনো কোনো রিপোর্ট নেই।")

conn.close()
