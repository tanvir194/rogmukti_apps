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
    st.stop()

# সাইডবারে লগআউট বাটন
st.sidebar.title(f"User: {st.session_state['user_role']}")
if st.sidebar.button("Log Out"):
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.rerun()
    # ডাটাবেজ কানেকশন
conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()

# নতুন ল্যাব রিপোর্ট টেবিল তৈরি (পুরানো বিলিং টেবিল অক্ষত থাকবে)
c.execute("CREATE TABLE IF NOT EXISTS test_reports (invoice_no TEXT PRIMARY KEY, test_name TEXT, result_values TEXT, status TEXT)")
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
    # ডাটাবেজে setup_doctors টেবিল না থাকলে এরর এড়াতে ট্রাই-ক্যাচ ব্যবহার করা হলো
    try:
        doctors_list = [row[0] for row in c.execute("SELECT name FROM setup_doctors").fetchall()]
    except:
        doctors_list = ["Self / Direct"]
    doc_filter = st.selectbox("Filter Doctor:", ["All Doctors"] + doctors_list)

# ডাটা লোড ও সেফ ক্যালকুলেশন (কলামের নাম পুরানো হোক বা নতুন, এরর আসবে না)
df_bills = pd.read_sql_query("SELECT * FROM bills", conn)

if not df_bills.empty:
    total_coll = df_bills['net_amount'].sum() if 'net_amount' in df_bills.columns else (df_bills['total_amount'].sum() if 'total_amount' in df_bills.columns else 0)
    total_disc = df_bills['discount'].sum() if 'discount' in df_bills.columns else 0
    total_paid = df_bills['paid_amount'].sum() if 'paid_amount' in df_bills.columns else (df_bills['paid'].sum() if 'paid' in df_bills.columns else 0)
    total_due = df_bills['due_amount'].sum() if 'due_amount' in df_bills.columns else (df_bills['due'].sum() if 'due' in df_bills.columns else 0)
    total_ref = df_bills['referral_fees'].sum() if 'referral_fees' in df_bills.columns else 0
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
query_sorted = "SELECT * FROM bills ORDER BY invoice_no DESC"
df_table = pd.read_sql_query(query_sorted, conn)

if not df_table.empty:
    # ডাটাবেজে যে কলামগুলোই থাকুক তা ডাইনামিক ফিল্টার করবে
    cols_to_show = [col for col in ['invoice_no', 'patient_name', 'referral_type', 'total_amount', 'paid_amount', 'due_amount', 'paid', 'due', 'tests'] if col in df_table.columns]
    df_display = df_table[cols_to_show]
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("No invoice data found.")
st.markdown("---")
col_form, col_print = st.columns(2)

with col_form:
    st.subheader("🧪 Lab Report Entry Form")
    search_inv = st.text_input("Enter Invoice Number to Add Report:", placeholder="INV-1780682177")
    
    if search_inv:
        # পুরানো ডাটাবেজে রোগীর নাম এবং টেস্ট কলাম ডাইনামিক খোঁজা
        c.execute("SELECT * FROM bills WHERE invoice_no=?", (search_inv,))
        patient_row = c.fetchone()
        
        if patient_row:
            # কলাম ইনডেক্স এরর এড়াতে ডাটাফ্রেম থেকে নাম তুলে আনা
            p_name = df_bills[df_bills['invoice_no']==search_inv]['patient_name'].values[0] if 'patient_name' in df_bills.columns else "Patient"
            p_tests = df_bills[df_bills['invoice_no']==search_inv]['tests'].values[0] if 'tests' in df_bills.columns else "General Tests"
            
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
        try:
            c.execute("SELECT r.test_name, r.result_values FROM test_reports r WHERE r.invoice_no = ?", (print_inv,))
            report_data = c.fetchone()
            
            if report_data:
                p_name = df_bills[df_bills['invoice_no']==print_inv]['patient_name'].values[0] if 'patient_name' in df_bills.columns else "Patient"
                p_tests, r_values = report_data
                st.success(f"Report Ready for {p_name}")
                
                pdf_bytes = generate_pdf_report(print_inv, p_name, p_tests, r_values)
                st.download_button(label="📥 Download PDF Report", data=pdf_bytes, file_name=f"Report_{print_inv}.pdf", mime="application/pdf")
            else:
                st.error("No approved report found for this Invoice.")
        except:
            st.error("Report processing error.")

# ডিলিট প্যানেল
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
# ==============================================================================
# পার্ট ৬: নতুন রোগীর মেমো তৈরি ও বিলিং সেকশন (New Billing & Invoice Generator)
# ==============================================================================
st.markdown("---")
st.subheader("🏥 Create New Patient Bill & Memo")

with st.form(key='new_billing_form', clear_on_submit=True):
    col_b1, col_b2, col_b3 = st.columns(3)
    
    with col_b1:
        # স্বয়ংক্রিয় ইউনিক ইনভয়েস নম্বর তৈরি
        generated_invoice = f"INV-{int(datetime.now().timestamp())}"
        st.info(f"**Generated Invoice No:** {generated_invoice}")
        patient_name = st.text_input("Patient Name:", placeholder="Enter full name")
        patient_phone = st.text_input("Mobile Number:", placeholder="01XXXXXXXXX")
        
    with col_b2:
        patient_age = st.text_input("Age:", placeholder="e.g. 25 Years")
        patient_gender = st.selectbox("Gender:", ["Male", "Female", "Others"])
        
        # ডাক্তার রেফারেল অপশন
        try:
            doc_options = [row[0] for row in c.execute("SELECT name FROM setup_doctors").fetchall()]
        except:
            doc_options = ["Self / Direct", "Dr. Saiful Islam", "Dr. Amit Das"]
        referred_doctor = st.selectbox("Referred Doctor:", doc_options)

    with col_b3:
        # টেস্ট নির্বাচন এবং কাস্টম প্রাইস লেখার সহজ উপায়
        st.write("**Select Tests & Enter Custom Prices:**")
        
        # ১. সিবিসি টেস্ট এবং প্রাইস
        cbc_check = st.checkbox("CBC")
        cbc_price = st.number_input("CBC Price (৳):", min_value=0, value=400, step=50) if cbc_check else 0
        
        # ২. ব্লাড গ্রুপ টেস্ট এবং প্রাইস
        bg_check = st.checkbox("Blood Group & Rh Factor")
        bg_price = st.number_input("Blood Group Price (৳):", min_value=0, value=200, step=50) if bg_check else 0
        
        # ৩. অন্য কোনো কাস্টম টেস্ট নিজে লেখার ব্যবস্থা (মেমোরি টেস্ট বা যেকোনো কিছু)
        custom_test_name = st.text_input("Custom Test Name (If any):", placeholder="e.g. Memory Test")
        custom_test_price = st.number_input("Custom Test Price (৳):", min_value=0, value=0, step=50) if custom_test_name else 0

    st.markdown("#### Bill Accounts Details")
    col_acc1, col_acc2, col_acc3 = st.columns(3)
    
    # টেস্টের মোট প্রাইস হিসাব করা
    selected_tests_list = []
    calculated_total = 0
    
    if cbc_check:
        selected_tests_list.append(f"CBC (৳{cbc_price})")
        calculated_total += cbc_price
    if bg_check:
        selected_tests_list.append(f"Blood Group (৳{bg_price})")
        calculated_total += bg_price
    if custom_test_name:
        selected_tests_list.append(f"{custom_test_name} (৳{custom_test_price})")
        calculated_total += custom_test_price
        
    all_selected_tests_string = ", ".join(selected_tests_list)

    with col_acc1:
        st.metric("Total Calculated Bill", f"৳ {calculated_total:,.2f}")
        discount_input = st.number_input("Discount Allowed (৳):", min_value=0, value=0)
        
    with col_acc2:
        net_payable = calculated_total - discount_input
        st.metric("Net Payable Amount", f"৳ {net_payable:,.2f}")
        paid_input = st.number_input("Paid Amount (৳):", min_value=0, value=0)
        
    with col_acc3:
        due_calculated = net_payable - paid_input
        st.metric("Total Due", f"৳ {due_calculated:,.2f}")
        ref_fee = st.number_input("Doctor Referral Commission (৳):", min_value=0, value=0)

    # সাবমিট বাটন যা ডাটাবেজে ডাটা সেভ করবে
    submit_bill_button = st.form_submit_button(label="💾 Save Bill & Print Memo")
    
    if submit_bill_button:
        if patient_name and all_selected_tests_string:
            current_date_str = datetime.now().strftime("%Y/%m/%d")
            
            # আপনার পুরানো ডাটাবেজের কলাম নামের সাথে সামঞ্জস্য রেখে সেভ করার চেষ্টা
            try:
                c.execute("""
                    INSERT INTO bills (invoice_no, date, patient_name, age, gender, phone, doctor, referral_type, referral_fees, total_amount, discount, net_amount, paid_amount, due_amount, tests) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (generated_invoice, current_date_str, patient_name, patient_age, patient_gender, patient_phone, referred_doctor, "Direct", ref_fee, calculated_total, discount_input, net_payable, paid_input, due_calculated, all_selected_tests_string))
                conn.commit()
                st.success(f"Success! Memo {generated_invoice} has been created and saved.")
                st.rerun()
            except Exception as e:
                # যদি পুরানো ডাটাবেজে কলামের নাম ভিন্ন থাকে তবে বিকল্প কোয়েরি দিয়ে ট্রাই করবে
                try:
                    c.execute("""
                        INSERT INTO bills (invoice_no, patient_name, total_amount, paid, due) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (generated_invoice, patient_name, calculated_total, paid_input, due_calculated))
                    conn.commit()
                    st.success(f"Success! Memo {generated_invoice} saved in legacy table.")
                    st.rerun()
                except Exception as legacy_error:
                    st.error(f"Database Save Error: {legacy_error}")
        else:
            st.warning("Please fill in the Patient Name and select at least one Test.")
        
