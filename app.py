import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime
from fpdf import FPDF

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")

# প্রফেশনাল সিএসএস স্টাইল
st.markdown("""
<style>
    .stTextInput input, .stSelectbox div[data-baseweb='select'], .stNumberInput input, .stMultiSelect div[data-baseweb='select'] {
        background-color: #f8f9fa !important; border: 1px solid #ced4da !important; border-radius: 6px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: bold !important; color: #0f4c81; }
    .main-header { color: #0f4c81; font-weight: bold; margin-bottom: 20px; }
    .billing-card { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e9ecef; }
</style>
""", unsafe_allow_html=True)

# সেশন স্টেট এবং পাসওয়ার্ড সিকিউরিটি
def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_role' not in st.session_state: st.session_state['user_role'] = None

# লগইন ইন্টারফেস স্ক্রিন
if not st.session_state['logged_in']:
    st.subheader("🔑 Login to Rogmukti Panel")
    username = st.text_input("User Name")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if username == "admin" and check_hashes(password, make_hashes("admin123")):
            st.session_state['logged_in'] = True; st.session_state['user_role'] = "Admin"; st.rerun()
        elif username == "labtech" and check_hashes(password, make_hashes("lab123")):
            st.session_state['logged_in'] = True; st.session_state['user_role'] = "Lab Technician"; st.rerun()
        else: st.error("Invalid Username or Password")
    st.stop()

# ডাটাবেজ কানেকশন ও রিপোর্ট টেবিল ইনিশিয়ালাইজেশন
conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS test_reports (invoice_no TEXT PRIMARY KEY, test_name TEXT, result_values TEXT, status TEXT)")
conn.commit()

# সাইডবার মাল্টি-পেজ নেভিগেশন মেনু
st.sidebar.title("🏥 Rogmukti Menu")
page = st.sidebar.radio("Go to Page:", ["📊 Dashboard & Reports", "💳 New Patient Billing"])
st.sidebar.markdown("---")
st.sidebar.write(f"Logged in as: **{st.session_state['user_role']}**")
if st.sidebar.button("🚪 Log Out"):
    st.session_state['logged_in'] = False; st.session_state['user_role'] = None; st.rerun()

# পিডিএফ রিপোর্ট মেকার ইঞ্জিন
def generate_pdf_report(invoice_no, patient_name, tests, results_str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20); pdf.set_text_color(15, 76, 129)
    pdf.cell(0, 10, "ROGMUKTI DIAGNOSTIC CENTRE", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10); pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "Hospital Road, Dhaka | Phone: +880123456789", ln=True, align="C")
    pdf.ln(5); pdf.set_draw_color(15, 76, 129); pdf.line(10, 30, 200, 30); pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "PATIENT MEDICAL REPORT", ln=True); pdf.set_font("Helvetica", "", 10)
    pdf.cell(100, 6, f"Invoice No: {invoice_no}"); pdf.cell(90, 6, f"Date: {datetime.now().strftime('%d-%b-%Y')}", ln=True)
    pdf.cell(100, 6, f"Patient Name: {patient_name}"); pdf.cell(90, 6, f"Tests: {tests}", ln=True); pdf.ln(8)
    pdf.set_fill_color(240, 240, 240); pdf.set_font("Helvetica", "B", 10)
    pdf.cell(70, 8, "Test Name", border=1, fill=True); pdf.cell(60, 8, "Observed Result", border=1, fill=True); pdf.cell(60, 8, "Reference Range", border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 10)
    for item in results_str.split(", "):
        if ":" in item:
            test_key, test_val = item.split(":", 1)
            normal_range = "12 - 16 g/dL" if "Hb" in test_key or "Hemoglobin" in test_key else "4,000 - 11,000"
            pdf.cell(70, 8, f" {test_key.strip()}", border=1)
            pdf.cell(60, 8, f" {test_val.strip()}", border=1)
            pdf.cell(60, 8, f" {normal_range}", border=1, ln=True)
    pdf.ln(20); pdf.cell(130, 6, ""); pdf.cell(60, 6, "_______________________", ln=True, align="C")
    pdf.cell(130, 6, ""); pdf.cell(60, 6, "Medical Officer Sign", ln=True, align="C")
    return pdf.output(dest="S")
    # ১. প্রথম পেজ: ড্যাশবোর্ড ও বিলিং ট্র্যাকিং লিস্ট
if page == "📊 Dashboard & Reports":
    st.markdown("<h2 class='main-header'>📊 Rogmukti Dashboard & Report Panel</h2>", unsafe_allow_html=True)
    
    # ডাইনামিক ডাটা ক্যালকুলেশন ও বাগ প্রোটেকশন
    df_bills = pd.read_sql_query("SELECT * FROM bills", conn)
    if not df_bills.empty:
        total_coll = df_bills['net_amount'].sum() if 'net_amount' in df_bills.columns else (df_bills['total_amount'].sum() if 'total_amount' in df_bills.columns else 0)
        total_paid = df_bills['paid_amount'].sum() if 'paid_amount' in df_bills.columns else (df_bills['paid'].sum() if 'paid' in df_bills.columns else 0)
        total_due = df_bills['due_amount'].sum() if 'due_amount' in df_bills.columns else (df_bills['due'].sum() if 'due' in df_bills.columns else 0)
        total_pat = len(df_bills)
    else: total_coll = total_paid = total_due = total_pat = 0

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total Collection", f"৳ {total_coll:,.2f}")
    col_m2.metric("Cash Received", f"৳ {total_paid:,.2f}")
    col_m3.metric("Total Due", f"৳ {total_due:,.2f}")
    col_m4.metric("Total Patients", f"{total_pat} Persons")

    st.markdown("---")
    st.subheader("📋 Latest Invoice & Billing Tracking (Sorted)")
    
    # নতুন ইনভয়েস সবার ওপরে দেখানোর জন্য কাস্টম কোয়েরি
    query_sorted = "SELECT * FROM bills ORDER BY invoice_no DESC"
    df_table = pd.read_sql_query(query_sorted, conn)
    if not df_table.empty:
        cols_to_display = [col for col in ['invoice_no', 'patient_name', 'total_amount', 'paid_amount', 'due_amount', 'paid', 'due', 'tests'] if col in df_table.columns]
        st.dataframe(df_table[cols_to_display], use_container_width=True)
    else: st.info("No data found in database table.")

    # ল্যাব রিপোর্ট এন্ট্রি ফর্ম ও ডাউনলোড এরিয়া
    st.markdown("---")
    col_left_form, col_right_print = st.columns(2)
    with col_left_form:
        st.subheader("🧪 Lab Report Entry")
        search_inv = st.text_input("Enter Invoice Number to Add Report:")
        if search_inv and not df_bills.empty and search_inv in df_bills['invoice_no'].values:
            with st.form(key='report_form_secure'):
                hb_val = st.text_input("Hemoglobin (Hb):")
                wbc_val = st.text_input("WBC Count:")
                if st.form_submit_button("Save Report"):
                    results_text = f"Hemoglobin: {hb_val} g/dL, WBC Count: {wbc_val}"
                    c.execute("INSERT OR REPLACE INTO test_reports VALUES (?, ?, ?, ?)", (search_inv, "General", results_text, "Approved"))
                    conn.commit(); st.success("Report Saved Successfully!")
                    
    with col_right_print:
        st.subheader("🖨️ Print / Download Report")
        print_inv = st.text_input("Enter Invoice Number to Print:")
        if print_inv:
            c.execute("SELECT r.test_name, r.result_values FROM test_reports r WHERE r.invoice_no = ?", (print_inv,))
            report_data = c.fetchone()
            if report_data and not df_bills.empty:
                patient_name_val = str(df_bills[df_bills['invoice_no']==print_inv]['patient_name'].values[0]) if 'patient_name' in df_bills.columns else "Patient"
                # এখানে ফিক্স করা হলো (প্যারামিটার সঠিকভাবে পাঠানো হয়েছে)
                pdf_bytes = generate_pdf_report(print_inv, patient_name_val, report_data[0], report_data[1])
                st.download_button("📥 Download PDF Report", data=pdf_bytes, file_name=f"Report_{print_inv}.pdf", mime="application/pdf")
            else: st.error("No approved report found for this invoice number.")
# ২. দ্বিতীয় পেজ: ১০০+ টেস্টের ড্রপডাউন এবং ডাইনামিক ক্যাশ মেমো জেনারেটর
if page == "💳 New Patient Billing":
    st.markdown("<h2 class='main-header'>💳 Create New Patient Bill & Memo</h2>", unsafe_allow_html=True)
    st.markdown("<div class='billing-card'>", unsafe_allow_html=True)
    
    with st.form(key='new_billing_form_clean_v3', clear_on_submit=True):
        gen_invoice = f"INV-{int(datetime.now().timestamp())}"
        st.markdown(f"<h4>Invoice No: <span style='color:#0f4c81;'>{gen_invoice}</span></h4>", unsafe_allow_html=True)
        st.markdown("---")
        
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            pat_name = st.text_input("Patient Full Name *", placeholder="Enter patient name")
            pat_phone = st.text_input("Mobile Number", placeholder="01XXXXXXXXX")
        with col_input2:
            pat_age = st.text_input("Age (e.g., 28 Years)")
            pat_gender = st.selectbox("Gender", ["Male", "Female", "Others"])
            
        st.markdown("---")
        col_doctor_panel, col_test_panel = st.columns(2)
        
        with col_doctor_panel:
            st.markdown("##### 🩺 Referred Doctor")
            try:
                db_doctors = [row for row in c.execute("SELECT name FROM setup_doctors").fetchall() if row]
                if not db_doctors or len(db_doctors) <= 1:
                    db_doctors = ["Self / Direct", "Dr. Saiful Islam", "Dr. Amit Das", "Dr. Nasrin Sultana", "Dr. Rahman Ali"]
            except:
                db_doctors = ["Self / Direct", "Dr. Saiful Islam", "Dr. Amit Das", "Dr. Nasrin Sultana", "Dr. Rahman Ali"]
            ref_doctor = st.selectbox("Select Referred Doctor:", db_doctors)

        with col_test_panel:
            st.markdown("##### 🧪 Select Diagnostic Tests (100+ Catalogue)")
            test_catalogue = {
