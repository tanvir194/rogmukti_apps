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

# A4 কাগজের জন্য টেবিল ফরম্যাটে ক্যাশ মেমো জেনারেটর পিডিএফ ইঞ্জিন
def generate_pdf_report(invoice_no, patient_name, tests_str, total, paid, due, disc=0, phone="-", age="-", gender="-"):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # হাসপাতালের হেডার (A4 স্ট্যান্ডার্ড)
    pdf.set_font("Helvetica", "B", 24); pdf.set_text_color(15, 76, 129)
    pdf.cell(0, 12, "ROGMUKTI DIAGNOSTIC CENTRE", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10); pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "Hospital Road, Dhaka | Phone: +880123456789 | Email: info@rogmukti.com", ln=True, align="C")
    pdf.ln(4); pdf.set_draw_color(15, 76, 129); pdf.set_line_width(0.5); pdf.line(10, 32, 200, 32); pdf.ln(6)
    
    # মেমোর টাইটেল ও রোগীর প্রফেশনাল ইনফো ব্লক
    pdf.set_font("Helvetica", "B", 14); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "INVOICE / CASH MEMO", ln=True); pdf.ln(2)
    
    pdf.set_font("Helvetica", "B", 10); pdf.set_text_color(50, 50, 50)
    pdf.cell(30, 6, "Invoice No:"); pdf.set_font("Helvetica", ""); pdf.cell(70, 6, str(invoice_no))
    pdf.set_font("Helvetica", "B"); pdf.cell(30, 6, "Date & Time:"); pdf.set_font("Helvetica", ""); pdf.cell(60, 6, datetime.now().strftime('%d-%b-%Y %I:%M %p'), ln=True)
    
    pdf.set_font("Helvetica", "B"); pdf.cell(30, 6, "Patient Name:"); pdf.set_font("Helvetica", ""); pdf.cell(70, 6, str(patient_name))
    pdf.set_font("Helvetica", "B"); pdf.cell(30, 6, "Mobile No:"); pdf.set_font("Helvetica", ""); pdf.cell(60, 6, str(phone), ln=True)
    
    pdf.set_font("Helvetica", "B"); pdf.cell(30, 6, "Age / Gender:"); pdf.set_font("Helvetica", ""); pdf.cell(70, 6, f"{age} / {gender}")
    pdf.set_font("Helvetica", "B"); pdf.cell(30, 6, "Referred By:"); pdf.set_font("Helvetica", ""); pdf.cell(60, 6, "Self / Direct", ln=True); pdf.ln(6)
    
    # টেবিল হেডার (SL No, Test, Price)
    pdf.set_fill_color(15, 76, 129); pdf.set_text_color(255, 255, 255); pdf.set_font("Helvetica", "B", 10)
    pdf.cell(20, 9, "SL No", border=1, fill=True, align="C")
    pdf.cell(120, 9, "Diagnostic Test Name", border=1, fill=True, align="L")
    pdf.cell(50, 9, "Price (TK)", border=1, fill=True, ln=True, align="R")
    
    # টেবিল ডাটা রো (Rows)
    pdf.set_text_color(0, 0, 0); pdf.set_font("Helvetica", "", 10)
    items = [x.strip() for x in tests_str.split(",") if x.strip()]
    sl = 1
    
    for item in items:
        if " (Tk" in item:
            t_name, t_pr = item.split(" (Tk")
            t_pr = t_pr.replace(")", "").strip()
        elif " (৳" in item:
            t_name, t_pr = item.split(" (৳")
            t_pr = t_pr.replace(")", "").strip()
        else:
            t_name, t_pr = item, "0"
            
        try: t_pr_float = float(t_pr)
        except: t_pr_float = 0.0
            
        pdf.cell(20, 8, str(sl), border=1, align="C")
        pdf.cell(120, 8, f" {t_name}", border=1, align="L")
        pdf.cell(50, 8, f"{t_pr_float:,.2f} ", border=1, ln=True, align="R")
        sl += 1
        
    pdf.ln(4)
    
    # রাইট অ্যালাইন্ড হিসাবপত্র
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(140, 6, "Total Amount:", align="R"); pdf.cell(50, 6, f"{float(total):,.2f} TK ", ln=True, align="R")
    if float(disc) > 0:
        pdf.cell(140, 6, "Discount Given:", align="R"); pdf.cell(50, 6, f"-{float(disc):,.2f} TK ", ln=True, align="R")
    pdf.cell(140, 6, "Paid Amount:", align="R"); pdf.cell(50, 6, f"{float(paid):,.2f} TK ", ln=True, align="R")
    pdf.set_draw_color(15, 76, 129); pdf.set_line_width(0.3); pdf.line(140, pdf.get_y()+1, 200, pdf.get_y()+1)
    pdf.cell(140, 8, "Remaining Due:", align="R"); pdf.cell(50, 8, f"{float(due):,.2f} TK ", ln=True, align="R")
    
    # A4 কাগজের নিচের দিকে সিগনেচার এরিয়া
    pdf.ln(25)
    pdf.cell(60, 6, "_______________________", align="C")
    pdf.cell(70, 6, "")
    pdf.cell(60, 6, "_______________________", ln=True, align="C")
    
    pdf.cell(60, 5, "Patient / Receiver Sign", align="C")
    pdf.cell(70, 5, "")
    pdf.cell(60, 5, "Authorized Accountant Sign", ln=True, align="C")
    
    return pdf.output(dest="S")

# ১. প্রথম পেজ: ড্যাশবোর্ড ও বিলিং ট্র্যাকিং লিস্ট
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
                    
    with col_right_print:
        st.subheader("🖨️ Print Reprints / Old Memo")
        print_inv = st.text_input("Enter Invoice Number to Reprint Memo:")
        if print_inv and not df_bills.empty and print_inv in df_bills['invoice_no'].values:
            p_col = 'patient_name' if 'patient_name' in df_bills.columns else ('name' if 'name' in df_bills.columns else df_bills.columns)
            p_row = df_bills[df_bills['invoice_no'] == print_inv]
            
            patient_name_val = str(p_row[p_col].values[0])
        
