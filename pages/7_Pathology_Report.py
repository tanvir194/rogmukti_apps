import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="AI Pathology Report", layout="wide")

st.title("🧠 AI Pathology Report Generator")
st.markdown("**আপনি শুধু টেস্ট সিলেক্ট করুন, AI অটো রিপোর্ট তৈরি করবে**")

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

tab1, tab2 = st.tabs(["🧠 AI রিপোর্ট জেনারেটর", "📋 সব রিপোর্ট"])

with tab1:
    st.subheader("নতুন AI রিপোর্ট তৈরি করুন")

    # Patient Info
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("রোগীর নাম *")
        patient_phone = st.text_input("মোবাইল নম্বর")
    with col2:
        doctor_name = st.text_input("রেফার করা ডাক্তার")
        report_date = st.date_input("রিপোর্টের তারিখ", datetime.now().date())

    # Test Selection
    common_tests = [
        "Blood Group + Rh", "HBsAg", "Random Blood Sugar (RBS)", 
        "Fasting Blood Sugar (FBS)", "CBC", "Lipid Profile", 
        "Serum Creatinine", "Urine R/M/E", "Liver Function Test (LFT)",
        "Thyroid Profile", "Others"
    ]
    
    test_name = st.selectbox("টেস্ট সিলেক্ট করুন", common_tests)

    st.markdown("### রেজাল্ট দিন")

    result_text = ""

    if test_name == "Blood Group + Rh":
        bg = st.selectbox("Blood Group", ["A", "B", "AB", "O"])
        rh = st.selectbox("Rh Factor", ["Positive (+VE)", "Negative (-VE)"])
        result_text = f"Blood Group : {bg}\nRh D type     : {rh}"

    elif test_name in ["Random Blood Sugar (RBS)", "Fasting Blood Sugar (FBS)"]:
        sugar = st.number_input("Sugar Level (mmol/L)", min_value=0.0, value=5.5, step=0.1)
        result_text = f"Random Blood Sugar : {sugar} mmol/L"

    elif test_name == "HBsAg":
        hbs = st.selectbox("HBsAg Result", ["Negative (-VE)", "Positive (+VE)"])
        result_text = f"HBsAg : {hbs}"

    elif test_name == "CBC":
        result_text = st.text_area("CBC রেজাল্ট লিখুন (যেমন: Hb, WBC, Platelet ইত্যাদি)", height=150)

    else:
        result_text = st.text_area("রেজাল্ট লিখুন", height=200)

    notes = st.text_area("অতিরিক্ত নোট / মন্তব্য (ঐচ্ছিক)", height=80)

    uploaded_file = st.file_uploader("অতিরিক্ত ফাইল আপলোড (ঐচ্ছিক)", 
                                   type=["pdf", "png", "jpg", "jpeg", "doc", "docx"])

    if st.button("🧠 AI রিপোর্ট জেনারেট ও সেভ করুন", type="primary", use_container_width=True):
        if patient_name and test_name and result_text:
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
                 doctor_name, result_text, notes, file_path))
            conn.commit()

            st.success("✅ AI রিপোর্ট সেভ হয়েছে!")

            # AI Generated Beautiful Report
            st.markdown("---")
            st.subheader("🖨️ প্রিন্ট রেডি AI রিপোর্ট")

            st.markdown(f"""
            <div style="border: 3px solid #1E88E5; padding: 30px; border-radius: 10px; background-color: #f8fdff;">
                <h2 style="text-align: center; color: #1E88E5;">Pathology Report</h2>
                <p><strong>রোগীর নাম :</strong> {patient_name} &nbsp;&nbsp; <strong>মোবাইল :</strong> {patient_phone}</p>
                <p><strong>রেফার ডাক্তার :</strong> {doctor_name} &nbsp;&nbsp; <strong>তারিখ :</strong> {report_date}</p>
                <p><strong>পরীক্ষা :</strong> {test_name}</p>
                <hr>
                <pre style="font-size: 17px; background:#f0f8ff; padding:15px; border-radius:8px;">{result_text}</pre>
                {f"<p><strong>মন্তব্য :</strong> {notes}</p>" if notes else ""}
                <br>
                <p style="text-align:right; color:#555;">Dr. Farjana Rashid Shammy<br>Pathologist</p>
            </div>
            """, unsafe_allow_html=True)

            st.info("↑ এই অংশটি সিলেক্ট করে **Ctrl + P** চাপুন প্রিন্ট করার জন্য")

with tab2:
    st.subheader("সকল রিপোর্ট")
    df = pd.read_sql_query("SELECT * FROM pathology_reports ORDER BY id DESC", conn)
    if not df.empty:
        for _, row in df.iterrows():
            with st.expander(f"{row['patient_name']} - {row['test_name']}"):
                st.write(f"**তারিখ:** {row['report_date']}")
                st.text_area("রেজাল্ট", row['result'], height=150, disabled=True)
                if row['file_path']:
                    fp = os.path.join(UPLOAD_FOLDER, row['file_path'])
                    if os.path.exists(fp):
                        with open(fp, "rb") as f:
                            st.download_button("📥 ডাউনলোড", f, row['file_path'])
    else:
        st.info("এখনো কোনো রিপোর্ট নেই")

conn.close()
