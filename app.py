import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime
from fpdf import FPDF
st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")
st.markdown("<style>.stTextInput input, .stSelectbox div[data-baseweb='select'], .stNumberInput input, .stMultiSelect div[data-baseweb='select'] { background-color: #f8f9fa !important; border: 1px solid #ced4da !important; border-radius: 6px !important; } div[data-testid='stMetricValue'] { font-size: 1.5rem !important; font-weight: bold !important; color: #0f4c81; } .main-header { color: #0f4c81; font-weight: bold; margin-bottom: 20px; } .billing-card { background-color: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e9ecef; }</style>", unsafe_allow_html=True)
def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text): return make_hashes(password) == hashed_text
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_role' not in st.session_state: st.session_state['user_role'] = None
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
conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS test_reports (invoice_no TEXT PRIMARY KEY, test_name TEXT, result_values TEXT, status TEXT)")
conn.commit()
st.sidebar.title("🏥 Rogmukti Menu")
page = st.sidebar.radio("Go to Page:", ["📊 Dashboard & Reports", "💳 New Patient Billing"])
st.sidebar.markdown("---")
st.sidebar.write(f"Logged in as: **{st.session_state['user_role']}**")
if st.sidebar.button("🚪 Log Out"):
st.session_state['logged_in'] = False; st.session_state['user_role'] = None; st.rerun()
if page == "📊 Dashboard & Reports":
st.markdown("<h2 class='main-header'>📊 Rogmukti Dashboard & Report Panel</h2>", unsafe_allow_html=True)
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
query_sorted = "SELECT * FROM bills ORDER BY invoice_no DESC"
df_table = pd.read_sql_query(query_sorted, conn)
if not df_table.empty:
p_col = 'patient_name' if 'patient_name' in df_table.columns else ('name' if 'name' in df_table.columns else df_table.columns)
cols_to_display = [col for col in ['invoice_no', p_col, 'total_amount', 'paid_amount', 'due_amount', 'paid', 'due', 'tests'] if col in df_table.columns]
st.dataframe(df_table[cols_to_display], use_container_width=True)
else: st.info("No data found in database table.")
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
if page == "💳 New Patient Billing":
st.markdown("<h2 class='main-header'>💳 Create New Patient Bill & Memo</h2>", unsafe_allow_html=True)
st.markdown("<div class='billing-card'>", unsafe_allow_html=True)
if 'last_saved_memo' not in st.session_state: st.session_state['last_saved_memo'] = None
with st.form(key='new_billing_form_clean_v5', clear_on_submit=False):
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
db_doctors = ["Self / Direct", "Dr. Saiful Islam", "Dr. Amit Das", "Dr. Nasrin Sultana", "Dr. Rahman Ali"]
ref_doctor = st.selectbox("Select Referred Doctor:", db_doctors)
with col_test_panel:
st.markdown("##### 🧪 Select Diagnostic Tests (100+ Catalogue)")
test_catalogue = {"CBC (Complete Blood Count)": 400, "Blood Grouping & Rh Factor": 200, "Serum Creatinine": 300, "HBsAg (Hepatitis B)": 350, "Lipid Profile": 1000, "CBC with ESR": 500, "Widal Test (Typhoid)": 400, "Uric Acid": 350, "Blood Sugar / Glucose (RBS/FBS)": 150, "Serum Bilirubin": 250, "SGPT / ALT": 350, "SGOT / AST": 350, "Serum Electrolytes": 900, "TSH (Thyroid)": 800, "Urine R/M/E": 200, "USG of Whole Abdomen": 1200, "X-Ray Chest P/A View": 500, "ECG (Electrocardiogram)": 400, "CRP (C-Reactive Protein)": 500, "Dengue NS1 Antigen": 600, "Memory Test (Custom)": 500}
selected_test_names = st.multiselect("Search & Select Multiple Tests:", list(test_catalogue.keys()))
total_bill = 0
tests_taken_list = []
if selected_test_names:
st.markdown("<div style='background-color:#f1f3f5; padding:10px; border-radius:5px;'><b>Selected Tests Price List:</b>", unsafe_allow_html=True)
for t_name in selected_test_names:
t_price = test_catalogue[t_name]
total_bill += t_price
tests_taken_list.append(f"{t_name} (৳{t_price})")
st.write(f"🔹 {t_name}: ৳ {t_price}")
st.markdown("</div>", unsafe_allow_html=True)
tests_string = ", ".join(tests_taken_list)
st.markdown("---")
st.markdown(f"### Total Calculated Amount: ৳ {total_bill:,.2f}")
col_acc1, col_acc2, col_acc3 = st.columns(3)
with col_acc1: disc_val = st.number_input("Discount Allowed (৳)", min_value=0, max_value=int(total_bill) if total_bill > 0 else 0, value=0)
with col_acc2:
payable_net = total_bill - disc_val
paid_val = st.number_input("Paid Amount (৳)", min_value=0, max_value=int(payable_net) if payable_net > 0 else 0, value=0)
with col_acc3:
due_val = payable_net - paid_val
st.write(f"**Remaining Due:** ৳ {due_val:,.2f}")
ref_commission = st.number_input("Doctor Referral Commission (৳)", min_value=0, value=0)
st.markdown("<br>", unsafe_allow_html=True)
save_clicked = st.form_submit_button(label="💾 Save Bill & Generate Memo")
if save_clicked:
if pat_name and tests_string:
cur_date = datetime.now().strftime("%Y/%m/%d")
db_table_info = pd.read_sql_query("SELECT * FROM bills LIMIT 1", conn)
cols_in_db = list(db_table_info.columns)
name_key = 'patient_name' if 'patient_name' in cols_in_db else ('name' if 'name' in cols_in_db else cols_in_db)
paid_key = 'paid_amount' if 'paid_amount' in cols_in_db else ('paid' if 'paid' in cols_in_db else 'paid_amount')
due_key = 'due_amount' if 'due_amount' in cols_in_db else ('due' if 'due' in cols_in_db else 'due_amount')
total_key = 'total_amount' if 'total_amount' in cols_in_db else ('total' if 'total' in cols_in_db else 'total_amount')
try:
if 'net_amount' in cols_in_db:
c.execute(f"INSERT INTO bills (invoice_no, date, {name_key}, age, gender, phone, doctor, referral_type, referral_fees, total_amount, discount, net_amount, {paid_key}, {due_key}, tests) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (gen_invoice, cur_date, pat_name, pat_age, pat_gender, pat_phone, ref_doctor, "Direct", ref_commission, total_bill, disc_val, payable_net, paid_val, due_val, tests_string))
else:
query_dynamic = f"INSERT INTO bills (invoice_no, {name_key}, {total_key}, {paid_key}, {due_key}"
values_list = [gen_invoice, pat_name, total_bill, paid_val, due_val]
if 'tests' in cols_in_db: query_dynamic += ", tests"; values_list.append(tests_string)
if 'date' in cols_in_db: query_dynamic += ", date"; values_list.append(cur_date)
query_dynamic += f") VALUES ({','.join(['?']*len(values_list))})"
c.execute(query_dynamic, tuple(values_list))
conn.commit()
st.session_state['last_saved_memo'] = {"inv": gen_invoice, "name": pat_name, "tests": tests_string, "total": total_bill, "paid": paid_val, "due": due_val, "disc": disc_val, "phone": pat_phone, "age": pat_age, "gender": pat_gender}
st.success(f"🎉 Bill Saved! Click below to print.")
except Exception as save_err: st.error(f"Database write error: {save_err}")
else: st.warning("Please input Patient Name and select at least one Test.")
if st.session_state['last_saved_memo'] is not None:
m_data = st.session_state['last_saved_memo']
pdf = FPDF(orientation='P', unit='mm', format='A4')
pdf.add_page()
pdf.set_font("Helvetica", "B", 24); pdf.set_text_color(15, 76, 129)
pdf.cell(0, 12, "ROGMUKTI DIAGNOSTIC CENTRE", ln=True, align="C")
pdf.set_font("Helvetica", "", 10); pdf.set_text_color(100, 100, 100)
pdf.cell(0, 5, "Hospital Road, Dhaka | Phone: +880123456789", ln=True, align="C")
pdf.ln(4); pdf.set_draw_color(15, 76, 129); pdf.set_line_width(0.5); pdf.line(10, 32, 200, 32); pdf.ln(6)
pdf.set_font("Helvetica", "B", 14); pdf.set_text_color(0, 0, 0)
pdf.cell(0, 8, "INVOICE / CASH MEMO", ln=True); pdf.ln(2)
pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(50, 50, 50)
pdf.cell(30, 6, "Invoice No:"); pdf.set_font("Helvetica", ""); pdf.cell(70, 6, str(m_data["inv"]))
pdf.set_font("Helvetica", "B"); pdf.cell(30, 6, "Date & Time:"); pdf.set_font("Helvetica", ""); pdf.cell(60, 6, datetime.now().strftime('%d-%b-%Y %I:%M %p'), ln=True)
pdf.cell(30, 6, "Patient Name:"); pdf.cell(70, 6, str(m_data["name"]))
pdf.set_font("Helvetica", "B"); pdf.cell(30, 6, "Mobile No:"); pdf.set_font("Helvetica", ""); pdf.cell(60, 6, str(m_data["phone"]), ln=True)
pdf.cell(30, 6, "Age / Gender:"); pdf.cell(70, 6, f"{m_data['age']} / {m_data['gender']}")
pdf.set_font("Helvetica", "B"); pdf.cell(30, 6, "Referred By:"); pdf.set_font("Helvetica", ""); pdf.cell(60, 6, "Self / Direct", ln=True); pdf.ln(6)
pdf.set_fill_color(15, 76, 129); pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 10)
pdf.cell(20, 9, "SL No", border=1, fill=True, align="C")
pdf.cell(120, 9, "Diagnostic Test Name", border=1, fill=True, align="L")
pdf.cell(50, 9, "Price (TK)", border=1, fill=True, ln=True, align="R")
pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", "", 10)
items = [x.strip() for x in m_data["tests"].split(",") if x.strip()]
sl = 1
for item in items:
if " (Tk" in item: t_name, t_pr = item.split(" (Tk")
elif " (৳" in item: t_name, t_pr = item.split(" (৳")
else: t_name, t_pr = item, "0"
t_pr = t_pr.replace(")", "").strip()
pdf.cell(20, 8, str(sl), border=1, align="C")
pdf.cell(120, 8, f" {t_name}", border=1, align="L")
pdf.cell(50, 8, f"{float(t_pr):,.2f} ", border=1, ln=True, align="R")
sl += 1
pdf.ln(4); pdf.set_font("Helvetica", "B", 10)
pdf.cell(140, 6, "Total Amount:", align="R"); pdf.cell(50, 6, f"{float(m_data['total']):,.2f} TK ", ln=True, align="R")
pdf.cell(140, 6, "Paid Amount:", align="R"); pdf.cell(50, 6, f"{float(m_data['paid']):,.2f} TK ", ln=True, align="R")
pdf.cell(140, 8, "Remaining Due:", align="R"); pdf.cell(50, 8, f"{float(m_data['due']):,.2f} TK ", ln=True, align="R")
pdf_bytes = pdf.output(dest="S")
st.markdown("---")
st.download_button(label="📥 PRINT / DOWNLOAD A4 CASH MEMO (PDF)", data=pdf_bytes, file_name=f"Rogmukti_Invoice_{m_data['inv']}.pdf", mime="application/pdf", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
