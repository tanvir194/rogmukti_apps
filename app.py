import streamlit as st, pandas as pd, sqlite3
from datetime import datetime, timedelta

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")

st.markdown("""
<style>
    .section-box-blue { background-color: #f1f8ff; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    .section-box-green { background-color: #f4faf6; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    .section-box-orange { background-color: #fff9f0; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    .stTextInput input { background-color: #e3f2fd !important; border: 1px solid #1e88e5 !important; color: black !important; font-weight: bold !important; }
    .stSelectbox div[data-baseweb='select'] { background-color: #e0f7fa !important; border: 1px solid #00bcd4 !important; font-weight: bold !important; }
    .stMultiSelect div[data-baseweb='select'] { background-color: #e8f5e9 !important; border: 1px solid #43a047 !important; font-weight: bold !important; }
    .stNumberInput input { background-color: #fffde7 !important; border: 1px solid #fbc02d !important; color: black !important; font-weight: bold !important; }
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: bold !important; color: #1e88e5 !important; }
    @media print { 
        body * { visibility: hidden !important; } 
        .print-area, .print-area * { visibility: visible !important; } 
        .print-area { position: absolute !important; left: 0 !important; top: 0 !important; width: 100% !important; margin: 0 !important; padding: 10px !important; border: none !important; } 
        [data-testid='stHeader'], button, iframe { display: none !important; } 
    }
</style>
""", unsafe_allow_html=True)

conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS bills (invoice_no TEXT PRIMARY KEY, date TEXT, patient TEXT, age TEXT, phone TEXT, doctor TEXT, total REAL, discount REAL, paid REAL, due REAL, referral_fee REAL)")
c.execute("CREATE TABLE IF NOT EXISTS setup_doctors (name TEXT UNIQUE)")
c.execute("CREATE TABLE IF NOT EXISTS setup_tests (name TEXT UNIQUE, rate REAL)")
conn.commit()

c.execute("SELECT COUNT(*) FROM setup_doctors")
if c.fetchone() == 0:
    for doc in ["Select Doctor", "Self / Direct", "Dr. Saiful Islam", "Dr. A. Rahman", "Dr. S. Islam"]:
        c.execute("INSERT OR IGNORE INTO setup_doctors VALUES (?)", (doc,))
    conn.commit()

c.execute("SELECT COUNT(*) FROM setup_tests")
if c.fetchone() == 0:
    default_tests = {
        "CBC": 400, "CBC with ESR": 600, "TC.DC": 250, "HB%": 250, "ESR": 200, "Platelet Count": 300,
        "Widal": 450, "CRP": 450, "Blood Group & Rh Factor": 200, "TSH": 1100, "Serum Creatinine": 400,
        "X-Ray Chest": 500, "Urine R/E": 250, "USG Whole Abdomen": 1000, "USG Color Doppler": 2500
    }
    for t_name, t_rate in default_tests.items():
        c.execute("INSERT OR IGNORE INTO setup_tests VALUES (?, ?)", (t_name, t_rate))
    conn.commit()

doctors_df = pd.read_sql_query("SELECT name FROM setup_doctors", conn)
doctors_list = doctors_df['name'].tolist()

tests_df = pd.read_sql_query("SELECT * FROM setup_tests", conn)
test_directory = dict(zip(tests_df['name'], tests_df['rate']))

tab1, tab2, tab3 = st.tabs(["📄 Billing / Cash Memo", "📊 Dashboard", "⚙️ Settings (যোগ ও পরিবর্তন)"])

with tab1:
    if "invoice_data" not in st.session_state: 
        st.session_state.invoice_data = None
        
    if st.session_state.invoice_data is None:
        st.markdown('<div class="section-box-blue">✨ <b>Patient Information & Doctor List (রোগী ও ডাক্তার তালিকা)</b></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            patient_name = st.text_input("Patient Name:")
            age = st.text_input("Age:")
            phone = st.text_input("Phone Number:")
        with col2:
            ref_dr = st.selectbox("Referred By:", doctors_list, key="billing_doctor_select")
            date_today = st.date_input("Date:", datetime.now())
            
        st.markdown('<div class="section-box-green">🔬 <b>Select Tests & Charges (টেস্ট নির্বাচন এবং ফি)</b></div>', unsafe_allow_html=True)
        available_tests = list(test_directory.keys())
        selected_tests = st.multiselect("Select Tests:", available_tests)
        
        total_amount, test_rows = 0.0, []
        for i, test in enumerate(selected_tests):
            price = test_directory[test]
            total_amount += price
            test_rows.append({"SL": i+1, "Test Name": test, "Rate (TK)": price})
            
        if selected_tests: 
            st.dataframe(pd.DataFrame(test_rows), use_container_width=True)
        
        st.markdown('<div class="section-box-orange">💰 <b>Payment & Calculation (পেমেন্ট এবং হিসাব)</b></div>', unsafe_allow_html=True)
        col3, col4, col5, col6 = st.columns(4)
        with col3: st.metric(label="Total Amount (মোট বিল):", value=f"TK {total_amount:,.2f}")
        with col4: discount = st.number_input("Discount (ছাড় TK):", min_value=0.0, step=10.0, value=0.0)
        with col5:
            net_total = max(0.0, total_amount - discount)
            paid = st.number_input("Paid Amount (জমা TK):", min_value=0.0, max_value=net_total, step=50.0, value=net_total)
        with col6:
            due = max(0.0, net_total - paid)
            st.metric(label="Due Amount (বাকি বিল):", value=f"TK {due:,.2f}")
            
        if st.button("Save Bill & Generate Invoice", key="save_bill_btn", type="primary"):
            if not patient_name: st.error("অনুগ্রহ করে রোগীর নাম লিখুন!")
            elif not selected_tests: st.error("অনুগ্রহ করে অন্তত একটি টেস্ট সিলেক্ট করুন!")
            else:
                invoice_no = f"INV-{int(datetime.now().timestamp())}"
                ref_fee = total_amount * 0.10
                c.execute("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (invoice_no, date_today.strftime('%Y-%m-%d'), patient_name, age, phone, ref_dr, total_amount, discount, paid, due, ref_fee))
                conn.commit()
                st.session_state.invoice_data = {"invoice_no": invoice_no, "date": date_today.strftime('%d-%m-%Y'), "name": patient_name, "age": age, "phone": phone, "dr": ref_dr, "tests": test_rows, "total": total_amount, "discount": discount, "paid": paid, "due": due}
                st.rerun()
    else:
        inv = st.session_state.invoice_data
        st.success(f"বিল সফলভাবে সেভ হয়েছে! ইনভয়েস নম্বর: {inv['invoice_no']}")
        
        rows_html = ""
        for row in inv['tests']: 
            rows_html += f"<tr><td style='padding: 6px; border: 1px solid #000;'>{row['SL']}</td><td style='padding: 6px; border: 1px solid #000;'>{row['Test Name']}</td><td style='padding: 6px; text-align: right; border: 1px solid #000;'>{row['Rate (TK)']}</td></tr>"
            
        html_bill = f"""
        <div class='print-area' style='width: 100%; max-width: 750px; padding: 20px; background-color: #ffffff; color: #000000; font-family: Arial, sans-serif; line-height: 1.3;'>
            <div style='text-align: center; margin-bottom: 15px;'>
                <h1 style='color: #ff0000; margin: 0; font-size: 26px; font-weight: bold;'>ROGMUKTI DIAGNOSTIC CENTRE</h1>
                <p style='margin: 4px 0 2px 0; font-size: 14px; font-weight: bold; color: #333333;'>Mollah Market, Galachipa, Patuakhali</p>
                <p style='margin: 0; font-size: 13px; font-weight: bold; color: #555555;'>Mobile: 01646176947</p>
                <div style='border-bottom: 2px double #000000; margin-top: 10px; margin-bottom: 8px;'></div>
                <span style='border: 1px solid #000; padding: 3px 15px; font-size: 13px; font-weight: bold; background-color: #f5f5f5;'>CASH MEMO / MONEY RECEIPT</span>
            </div>
            <table style="width: 100%; margin-bottom: 15px; font-size: 14px;">
                <tr><td><b>Patient Name:</b> {inv['name']}</td><td><b>Invoice No:</b> {inv['invoice_no']}</td></tr>
                <tr><td><b>Age:</b> {inv['age']} | <b>Phone:</b> {inv['phone']}</td><td><b>Date:</b> {inv['date']}</td></tr>
                <tr><td colspan='2'><b>Referred By:</b> {inv['dr']}</td></tr>
            </table>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 14px;">
                <thead><tr style="background-color: #f2f2f2;"><th style="border: 1px solid #000; padding: 6px;">SL</th><th style="border: 1px solid #000; padding: 6px;">Test Name</th><th style="border: 1px solid #000; padding: 6px; text-align: right;">Rate (TK)</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            <div style="float: right; width: 250px; font-size: 14px;">
                <table style="width: 100%;">
                    <tr><td>Total Amount:</td><td style="text-align: right;">{inv['total']:.2f}</td></tr>
                    <tr><td>Discount:</td><td style="text-align: right;">{inv['discount']:.2f}</td></tr>
                    <tr><td><b>Net Payable:</b></td><td style="text-align: right;"><b>{(inv['total']-inv['discount']):.2f}</b></td></tr>
                    <tr><td>Paid Amount:</td><td style="text-align: right;">{inv['paid']:.2f}</td></tr>
                    <tr style="border-top: 1px solid #000;"><td><b>Due Amount:</b></td><td style="text-align: right; color: red;"><b>{inv['due']:.2f}</b></td></tr>
                </table>
            </div>
            <div style="clear: both; margin-top: 50px;"><p style="float: left; border-top: 1px solid #000; width: 150px; text-align: center;">Prepared By</p><p style="float: right; border-top: 1px solid #000; width: 150px; text-align: center;">Authorized Signatory</p></div>
        </div>
        """
        st.markdown(html_bill, unsafe_allow_html=True)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("Print Invoice (প্রিন্ট করুন)"):

