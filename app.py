import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, timedelta
from fpdf import FPDF

# ১. পেজ কনফিগারেশন ও ইংরেজি টাইটেল সেট করা হলো
st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")

# সিএসএস স্টাইল এবং প্রিন্ট লেআউট
st.markdown("""
<style>
    .section-box-blue { background-color: #f1f8ff; padding: 12px; border-radius: 8px; margin-bottom: 10px; }
    .section-box-green { background-color: #f4faf6; padding: 12px; border-radius: 8px; margin-bottom: 10px; }
    .section-box-orange { background-color: #fff9f0; padding: 12px; border-radius: 8px; margin-bottom: 10px; }
    .stTextInput input { background-color: #e3f2fd !important; border: 1px solid #90caf9 !important; }
    .stSelectbox div[data-baseweb='select'] { background-color: #e0f7fa !important; }
    .stMultiSelect div[data-baseweb='select'] { background-color: #e8f5e9 !important; }
    .stNumberInput input { background-color: #fffde7 !important; border: 1px solid #fff59d !important; }
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: bold !important; }
    @media print {
        body * { visibility: hidden !important; }
        .print-area, .print-area * { visibility: visible !important; }
        .print-area { position: absolute !important; left: 0 !important; top: 0 !important; width: 100% !important; }
        [data-testid='stHeader'], button, iframe { display: none !important; }
    }
</style>
""", unsafe_allow_html=True)
# পাসওয়ার্ড হ্যাশ করার ফাংশন
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# সেশন স্টেট তৈরি (লগইন স্ট্যাটাস ধরে রাখার জন্য)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

# লগইন স্ক্রিন ইন্টারফেস
if not st.session_state['logged_in']:
    st.subheader("🔑 Login to Rogmukti Panel")
    username = st.text_input("User Name")
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        if username == "admin" and check_hashes(password, make_hashes("admin123")):
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = "Admin"
            st.success("Logged in as Admin")
            st.rerun()
        elif username == "labtech" and check_hashes(password, make_hashes("lab123")):
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = "Lab Technician"
            st.success("Logged in as Lab Technician")
            st.rerun()
        else:
            st.error("Invalid Username or Password")
    st.stop() # লগইন না হওয়া পর্যন্ত নিচের কোনো কোড দেখাবে না

# সাইডবারে লগআউট বাটন
st.sidebar.title(f"User: {st.session_state['user_role']}")
if st.sidebar.button("Log Out"):
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.rerun()
# ডাটাবেজ কানেকশন
conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()

# টেবিল তৈরি (নতুন রিপোর্ট টেবিল সহ)
c.execute("CREATE TABLE IF NOT EXISTS bills (invoice_no TEXT PRIMARY KEY, date TEXT, patient_name TEXT, age TEXT, gender TEXT, phone TEXT, doctor TEXT, referral_type TEXT, referral_fees REAL, total_amount REAL, discount REAL, net_amount REAL, paid_amount REAL, due_amount REAL, tests TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS setup_doctors (name TEXT UNIQUE)")
c.execute("CREATE TABLE IF NOT EXISTS setup_tests (name TEXT UNIQUE, rate REAL)")
c.execute("CREATE TABLE IF NOT EXISTS test_reports (invoice_no TEXT PRIMARY KEY, test_name TEXT, result_values TEXT, status TEXT)")
conn.commit()

# ডিফল্ট ডাটা ইনসার্ট (ইংরেজি)
c.execute("SELECT COUNT(*) FROM setup_doctors")
if c.fetchone() == 0:
    for doc in ["Select Doctor", "Self / Direct", "Dr. Saiful Islam", "Dr. Amit Das"]:
        c.execute("INSERT OR IGNORE INTO setup_doctors VALUES (?)", (doc,))
    conn.commit()

c.execute("SELECT COUNT(*) FROM setup_tests")
if c.fetchone() == 0:
    default_tests = {
        "CBC": 400, "CBC with ESR": 600, "TC.DC": 250, "HB%": 250, "ESR": 200,
        "Widal": 450, "CRP": 450, "Blood Group & Rh Factor": 200, "TSH": 1100,
        "X-Ray Chest": 500, "Urine R/E": 250, "USG Whole Abdomen": 1000
    }
    for t_name, t_rate in default_tests.items():
        c.execute("INSERT OR IGNORE INTO setup_tests VALUES (?, ?)", (t_name, t_rate))
    conn.commit()

# পিডিএফ জেনারেটর ফাংশন
def generate_pdf_report(invoice_no, patient_name, tests, results_str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "ROGMUKTI DIAGNOSTIC CENTRE", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "Hospital Road, Dhaka, Bangladesh | Phone: +880123456789", ln=True, align="C")
    pdf.ln(5)
    pdf.set_draw_color(0, 102, 204)
    pdf.line(10, 30, 200, 30)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "PATIENT MEDICAL REPORT", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(100, 6, f"Invoice No: {invoice_no}", border=0)
    pdf.cell(90, 6, f"Date: {datetime.now().strftime('%d-%b-%Y')}", border=0, ln=True)
    pdf.cell(100, 6, f"Patient Name: {patient_name}", border=0)
    pdf.cell(90, 6, f"Tests: {tests}", border=0, ln=True)
    pdf.ln(8)
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(70, 8, "Test Name", border=1, fill=True)
    pdf.cell(60, 8, "Observed Result", border=1, fill=True)
    pdf.cell(60, 8, "Normal Reference Range", border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 10)
    items = results_str.split(", ")
    for item in items:
        if ":" in item:
            test_key, test_val = item.split(":", 1)
            normal_range = "N/A"
            if "Hb" in test_key or "Hemoglobin" in test_key: normal_range = "12 - 16 g/dL"
            elif "WBC" in test_key: normal_range = "4,000 - 11,000 /cu.mm"
            pdf.cell(70, 8, f" {test_key.strip()}", border=1)
            pdf.cell(60, 8, f" {test_val.strip()}", border=1)
            pdf.cell(60, 8, f" {normal_range}", border=1, ln=True)
    pdf.ln(20)
    pdf.cell(130, 6, "", border=0)
    pdf.cell(60, 6, "_______________________", border=0, ln=True, align="C")
    pdf.cell(130, 6, "", border=0)
    pdf.cell(60, 6, "Medical Officer / Pathologist", border=0, ln=True, align="C")
    return pdf.output(dest="S")
st.title("📊 Rogmukti Dashboard & Report Panel")

# ফিল্টার সেকশন
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    time_filter = st.selectbox("Filter Time:", ["All Time", "Today", "Custom Date"])
with col_f2:
    search_date = st.date_input("Select Date:", datetime.now().date())
with col_f3:
    doc_filter = st.selectbox("Filter Doctor:", ["All Doctors"] + [row[0] for row in c.execute("SELECT name FROM setup_doctors").fetchall()])

# ডাটা লোড ও ক্যালকুলেশন
df_bills = pd.read_sql_query("SELECT * FROM bills", conn)

if not df_bills.empty:
    total_coll = df_bills['net_amount'].sum()
    total_disc = df_bills['discount'].sum()
    total_paid = df_bills['paid_amount'].sum()
    total_due = df_bills['due_amount'].sum()
    total_ref = df_bills['referral_fees'].sum()
    total_pat = len(df_bills)
else:
    total_coll = total_disc = total_paid = total_due = total_ref = total_pat = 0

# মেট্রিক কার্ড ডিসপ্লে
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Collection", f"৳ {total_coll:,.2f}")
c2.metric("Total Discount", f"৳ {total_disc:,.2f}")
c3.metric("Cash Received", f"৳ {total_paid:,.2f}")
c4.metric("Total Due", f"৳ {total_due:,.2f}")
c5.metric("Referral Fee", f"৳ {total_ref:,.2f}")
c6.metric("Total Patients", f"{total_pat} Persons")

st.markdown("---")
st.subheader("📋 Today's Latest Test Booking & Billing Tracking")

# ORDER BY invoice_no DESC দিয়ে ইনভয়েস ক্রমানুসারে নতুনগুলো ওপরে সাজানো হলো
query_sorted = "SELECT invoice_no, patient_name, referral_type, total_amount, paid_amount, due_amount FROM bills ORDER BY invoice_no DESC"
df_table = pd.read_sql_query(query_sorted, conn)
df_table.columns = ["Invoice No", "Patient Name", "Referral Type", "Total Bill (৳)", "Paid (৳)", "Due (৳)"]

st.dataframe(df_table, use_container_width=True)
st.markdown("---")
# দুটি কলাম তৈরি করে একপাশে এন্ট্রি ফর্ম এবং অন্যপাশে ডাউনলোড অপশন রাখা হলো
col_form, col_print = st.columns(2)

with col_form:
    st.subheader("🧪 Lab Report Entry Form")
    search_inv = st.text_input("Enter Invoice Number to Add Report:", placeholder="INV-1780682177")
    
    if search_inv:
        c.execute("SELECT invoice_no, patient_name, tests FROM bills WHERE invoice_no=?", (search_inv,))
        patient_data = c.fetchone()
        if patient_data:
            inv, p_name, p_tests = patient_data
            st.info(f"**Patient:** {p_name} | **Tests:** {p_tests}")
            
            with st.form(key='report_form'):
                hemoglobin = st.text_input("Hemoglobin (Hb) (Normal: 12-16 g/dL)")
                wbc_count = st.text_input("Total WBC Count (Normal: 4000-11000 /cu.mm)")
                submit_report = st.form_submit_button(label="Save Report")
                
                if submit_report:
                    results = f"Hemoglobin: {hemoglobin} g/dL, WBC Count: {wbc_count}"
                    c.execute("INSERT OR REPLACE INTO test_reports VALUES (?, ?, ?, ?)", (search_inv, p_tests, results, "Approved"))
                    conn.commit()
                    st.success(f"Report saved for {search_inv}!")
        else:
            st.error("Invoice not found!")

with col_print:
    st.subheader("🖨️ Print / Download Report")
    print_inv = st.text_input("Enter Invoice Number to Print:", placeholder="INV-1780682177", key="print_key")
    
    if print_inv:
        c.execute("SELECT b.patient_name, b.tests, r.result_values FROM bills b JOIN test_reports r ON b.invoice_no = r.invoice_no WHERE b.invoice_no = ?", (print_inv,))
        report_data = c.fetchone()
        if report_data:
            p_name, p_tests, r_values = report_data
            st.success(f"Report Ready for {p_name}")
            
            # পিডিএফ জেনারেট ও ডাউনলোড বাটন
            pdf_bytes = generate_pdf_report(print_inv, p_name, p_tests, r_values)
            st.download_button(label="📥 Download PDF Report", data=pdf_bytes, file_name=f"Report_{print_inv}.pdf", mime="application/pdf")
        else:
            st.error("No approved report found.")

# ডিলিট প্যানেল (অ্যাডমিন রোল থাকলে শুধু কাজ করবে)
st.markdown("---")
st.subheader("🗑️ Admin Settings & Invoice Delete Panel")
if st.session_state['user_role'] == "Admin":
    del_invoice = st.text_input("Invoice Number to Delete:", placeholder="INV-000000")
    if st.button("🔴 Delete Invoice"):
        if del_invoice:
            c.execute("DELETE FROM bills WHERE invoice_no=?", (del_invoice,))
            c.execute("DELETE FROM test_reports WHERE invoice_no=?", (del_invoice,))
            conn.commit()
            st.success(f"Invoice {del_invoice} deleted!")
            st.rerun()
else:
    st.warning("Only Admins can delete invoices.")
