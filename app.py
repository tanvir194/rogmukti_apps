import streamlit as st, pandas as pd, sqlite3
from datetime import datetime, timedelta
st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")
st.markdown("<style>.section-box-blue { background-color: #f1f8ff; padding: 12px; border-radius: 5px; margin-bottom: 10px; }.section-box-green { background-color: #f4faf6; padding: 12px; border-radius: 5px; margin-bottom: 10px; }.section-box-orange { background-color: #fff9f0; padding: 12px; border-radius: 5px; margin-bottom: 10px; }.stTextInput input { background-color: #e3f2fd !important; border: 1px solid #1e88e5 !important; color: black !important; font-weight: bold !important; }.stSelectbox div[data-baseweb='select'] { background-color: #e0f7fa !important; border: 1px solid #00bcd4 !important; font-weight: bold !important; }.stMultiSelect div[data-baseweb='select'] { background-color: #e8f5e9 !important; border: 1px solid #43a047 !important; font-weight: bold !important; }.stNumberInput input { background-color: #fffde7 !important; border: 1px solid #fbc02d !important; color: black !important; font-weight: bold !important; } @media print { body * { visibility: hidden !important; } .print-area, .print-area * { visibility: visible !important; } .print-area { position: absolute !important; left: 0 !important; top: 0 !important; width: 100% !important; margin: 0 !important; padding: 10px !important; border: none !important; } [data-testid='stHeader'], button, iframe { display: none !important; } }</style>", unsafe_allow_html=True)
doctors_list = ["Select Doctor", "Self / Direct", "Dr. Saiful Islam", "Dr. A. Rahman", "Dr. S. Islam"]
test_directory = {
    "Select Test": 0, "CBC": 400, "CBC with ESR": 600, "TC.DC": 250, "HB%": 250, "ESR": 200, "Platelet Count": 300, "MP": 200, "BT/CT": 350, "C/E Count": 250,
    "Widal": 450, "Aso Titre": 450, "CRP": 450, "RA/RF": 450, "HBs Ag (Screen Test)": 450, "TPHA": 450, "VDRL": 400, "Blood Group & Rh Factor": 200, "Mantaux-Test (M.T)": 200, "Triple Antigen": 500, "HIV": 450, "HCV": 500, "TB (ICT)": 750, "Malaria. pf/pv": 700, "H. Pylori": 850, "Filaria (ICT)": 750, "Dengue NS1. IGG/IgM": 300,
    "T3": 1200, "T4": 1200, "FT3": 900, "FT4": 900, "TSH": 1100, "HbA1c": 1500, "Prolactin": 1200, "S. IgE": 1500, "S.IgE (Device Test)": 700,
    "Random Blood Sugar": 200, "Fasting Blood Sugar": 200, "2hr. After Breakfast (2HAB)": 200, "2hr. After 75gm Glucose": 200, "O.G.T.T": 500, "Blood Urea": 400, "Cholesterol": 350, "HDL": 400, "TG": 350, "LDL": 300, "S.GPT (ALT)": 500, "S.GOT (AST)": 500, "Bilirubin Total": 350, "Lipid Profile": 1000, "Bilirubin Direct/Indirect": 450, "Serum Creatinine": 400, "Uric Acid": 400, "Amylase": 700, "Calcium": 600,
    "X-Ray Chest": 500, "X-Ray PNS": 500, "X-Ray Maxilla": 500, "X-Ray Nasopharynx": 550, "X-Ray Abdomen A/P": 500, "X-Ray Cervical Spine": 600, "X-Ray Plane X-Ray Abdomen": 500, "X-Ray Mastoid Towns View": 500, "X-Ray Skull": 600, "X-Ray Pelvic": 500, "X-Ray Mandible B/V": 600, "X-Ray KUB": 500, "X-Ray D/S Spine": 600, "X-Ray L/S Spine": 600, "X-Ray Foot B/V": 500, "X-Ray Knee B/V": 550, "X-Ray Elbow B/V": 500, "X-Ray Shoulder Joint B/V": 550, "X-Ray Hip Joint": 500,
    "Urine Pregnancy Test (PT)": 200, "Urine R/E": 250, "Stool R/E": 400, "Stool OBT": 400, "USG Whole Abdomen": 1000, "USG Upper Abdomen": 800, "USG Lower Abdomen": 800, "USG KUB": 1000, "USG Pregnancy Profile": 800, "USG Breast": 1200, "USG Color Doppler": 2500
}
conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS bills (invoice_no TEXT PRIMARY KEY, date TEXT, patient TEXT, age TEXT, phone TEXT, doctor TEXT, total REAL, discount REAL, paid REAL, due REAL, referral_fee REAL)")
conn.commit()
tab1, tab2 = st.tabs(["📄 Billing / Cash Memo", "📊 Dashboard"])
with tab1:
    if "invoice_data" not in st.session_state: st.session_state.invoice_data = None
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
        available_tests = [test for test in test_directory.keys() if test != "Select Test"]
        selected_tests = st.multiselect("Select Tests:", available_tests)
        total_amount, test_rows = 0.0, []
        for i, test in enumerate(selected_tests):
            price = test_directory[test]
            total_amount += price
            test_rows.append({"SL": i+1, "Test Name": test, "Rate (TK)": price})
        if selected_tests: st.dataframe(pd.DataFrame(test_rows), use_container_width=True)
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
                ref_fee = total_amount * 0.30
                c.execute("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (invoice_no, date_today.strftime('%Y-%m-%d'), patient_name, age, phone, ref_dr, total_amount, discount, paid, due, ref_fee))
                conn.commit()
                st.session_state.invoice_data = {"invoice_no": invoice_no, "date": date_today.strftime('%d-%m-%Y'), "name": patient_name, "age": age, "phone": phone, "dr": ref_dr, "tests": test_rows, "total": total_amount, "discount": discount, "paid": paid, "due": due}
                st.rerun()
    else:
        inv = st.session_state.invoice_data
        st.success(f"বিল সফলভাবে সেভ হয়েছে! ইনভয়েস নম্বর: {inv['invoice_no']}")
        rows_html = ""
        for row in inv['tests']: rows_html += f"<tr><td style='padding: 6px; border: 1px solid #000;'>{row['SL']}</td><td style='padding: 6px; border: 1px solid #000;'>{row['Test Name']}</td><td style='padding: 6px; text-align: right; border: 1px solid #000;'>{row['Rate (TK)']}</td></tr>"
        html_bill = f"<div class='print-area' style='width: 100%; max-width: 750px; padding: 20px; background-color: #ffffff; color: #000000; font-family: Arial, sans-serif; line-height: 1.3;'><div style='text-align: center; margin-bottom: 15px;'><h1 style='color: #ff0000; margin: 0; font-size: 26px; font-weight: bold;'>ROGMUKTI DIAGNOSTIC CENTRE</h1><p style='margin: 4px 0 2px 0; font-size: 14px; font-weight: bold; color: #333333;'>Mollah Market, Galachipa, Patuakhali</p><p style='margin: 0; font-size: 13px; font-weight: bold; color: #555555;'>Mobile: 01646176947</p><div style='border-bottom: 2px double #000000; margin-top: 10px; margin-bottom: 8px;'></div><span style='border: 1px solid #000; padding: 3px 15px; font-size: 13px; font-weight: bold; background-color: #f5f5f5;'>CASH MEMO / MONEY RECEIPT</span></div><table style=\"width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 14px; color: #000000;\"><tr><td style='padding: 4px; width: 15%; font-weight: bold;'>Invoice No:</td><td style='padding: 4px; width: 35%; border-bottom: 1px dotted #000;'>{inv['invoice_no']}</td><td style='padding: 4px; width: 15%; font-weight: bold; text-align: right;'>Date:</td><td style='padding: 4px; width: 35%; border-bottom: 1px dotted #000; text-align: center;'>{inv['date']}</td></tr><tr><td style='padding: 4px; font-weight: bold;'>Patient Name:</td><td style='padding: 4px; border-bottom: 1px dotted #000; font-weight: bold;'>{inv['name']}</td><td style='padding: 4px; font-weight: bold; text-align: right;'>Age/Sex:</td><td style='padding: 4px; border-bottom: 1px dotted #000; text-align: center;'>{inv['age']}</td></tr><tr><td style='padding: 4px; font-weight: bold;'>Mobile No:</td><td style='padding: 4px; border-bottom: 1px dotted #000;'>{inv['phone']}</td><td style='padding: 4px; font-weight: bold; text-align: right;'>Ref. By:</td><td style='padding: 4px; border-bottom: 1px dotted #000; font-weight: bold; text-align: center;'>{inv['dr']}</td></tr></table><div style='border-bottom: 1px solid #000000; margin-bottom: 10px;'></div><p style='margin: 0 0 5px 0; font-weight: bold; font-size: 14px;'>🔬 INVESTIGATION LIST (টেস্টের বিবরণ):</p><table style='width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 14px;'><tr style='background-color: #f5f5f5; border-top: 1px solid #000; border-bottom: 1px solid #000;'><th style='padding: 6px; text-align: left; width: 12%; border: 1px solid #000;'>SL</th><th style='padding: 6px; text-align: left; width: 63%; border: 1px solid #000;'>Test Name</th><th style='padding: 6px; text-align: right; width: 25%; border: 1px solid #000;'>Rate (TK)</th></tr>{rows_html}</table><table style='width: 100%; font-size: 15px; font-weight: bold; border-collapse: collapse; margin-top: 10px;'><tr style='border-top: 2px solid #000; border-bottom: 2px solid #000;'><td>Total: TK {inv['total']}</td><td style='padding: 8px 5px; color: blue;'>Discount: TK {inv['discount']}</td><td style='padding: 8px 5px; color: green;'>Paid: TK {inv['paid']}</td><td style='padding: 8px 5px; color: red;'>Due: TK {inv['due']}</td></tr></table><div style='margin-top: 60px; display: flex; justify-content: space-between; font-size: 13px;'><p style='border-top: 1px solid #000; width: 150px; text-align: center; margin: 0; color: #000000;'>Prepared By</p><p style='border-top: 1px solid #000; width: 150px; text-align: center; margin: 0; color: #000000;'>Authorized Signature</p></div></div>"
        st.html(html_bill)
        st.components.v1.html("<button onclick='parent.window.print();' style='background-color: #00E676; color: black; padding: 14px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%; font-family: sans-serif;'>🖨️ ১-ক্লিকে রসিদ প্রিন্ট / PDF সেভ করুন</button>", height=60)
        if st.button("🆕 নতুন রোগীর বিল তৈরি করুন", type="secondary", use_container_width=True):
            st.session_state.invoice_data = None
            st.rerun()
with tab2:
    st.markdown("<h2 style='text-align: center; color: #1E88E5;'>📊 রোগমুক্তি ড্যাশবোর্ড ও রিপোর্ট প্যানেল</h2>", unsafe_allow_html=True)
    try:
        df_dash = pd.read_sql_query("SELECT * FROM bills", conn)
        if not df_dash.empty:
            df_dash['date'] = pd.to_datetime(df_dash['date'], errors='coerce')
            col_f1, col_f2 = st.columns(2)
            with col_f1: f_opt = st.selectbox("📅 সময় নির্বাচন করুন:", ["সব সময়", "আজ", "এই সপ্তাহ", "এই মাস", "এই বছর"], key="dash_time_f_unique")
            with col_f2:
                all_docs = ["সব ডাক্তার"] + [d for d in doctors_list if d != "Select Doctor"]
                f_doc = st.selectbox("👨‍⚕️ ডাক্তার নির্বাচন করুন:", all_docs, key="dash_doc_f_unique")
            t_now = datetime.today()
            if f_opt == "আজ": f_df = df_dash[df_dash['date'].dt.date == t_now.date()]
            elif f_opt == "এই সপ্তাহ": f_df = df_dash[df_dash['date'] >= (t_now - timedelta(days=t_now.weekday()))]
            elif f_opt == "এই মাস": f_df = df_dash[(df_dash['date'].dt.month == t_now.month) & (df_dash['date'].dt.year == t_now.year)]
            elif f_opt == "এই বছর": f_df = df_dash[df_dash['date'].dt.year == t_now.year]
            else: f_df = df_dash
            if f_doc != "সব ডাক্তার": f_df = f_df[f_df['doctor'] == f_doc]

