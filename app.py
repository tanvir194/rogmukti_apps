import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")

# ইনপুট বক্স ও সেকশন রঙিন করার CSS
st.markdown("""
<style>
    .section-box-blue { background-color: #f1f8ff; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    .section-box-green { background-color: #f4faf6; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    .section-box-orange { background-color: #fff9f0; padding: 12px; border-radius: 5px; margin-bottom: 10px; }

    .stTextInput input { background-color: #e3f2fd !important; border: 1px solid #1e88e5 !important; color: black !important; font-weight: bold !important; }
    .stSelectbox div[data-baseweb="select"] { background-color: #e0f7fa !important; border: 1px solid #00bcd4 !important; font-weight: bold !important; }
    .stMultiSelect div[data-baseweb="select"] { background-color: #e8f5e9 !important; border: 1px solid #43a047 !important; font-weight: bold !important; }
    .stNumberInput input { background-color: #fffde7 !important; border: 1px solid #fbc02d !important; color: black !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Market, Galachipa, Patuakhali</p>", unsafe_allow_html=True)

# ডাক্তারদের তালিকা
doctors_list = ["Select Doctor", "Self / Direct", "Dr. Saiful Islam", "Dr. A. Rahman", "Dr. S. Islam"]
# টেস্টের বড় তালিকা এবং অফিশিয়াল সঠিক দামের ডিরেক্টরি (ছবি অনুসারে)
test_directory = {
    "Select Test": 0,
    # --- HAEMATOLOGY ---
    "CBC": 400, "CBC with ESR": 600, "TC.DC": 250, "HB%": 250, "ESR": 200, "Platelet Count": 300, "MP": 200, "BT/CT": 350, "C/E Count": 250,
    
    # --- SEROLOGY ---
    "Widal": 450, "Aso Titre": 450, "CRP": 450, "RA/RF": 450, "HBs Ag (Screen Test)": 450, "TPHA": 450, "VDRL": 400, "Blood Group & Rh Factor": 200, "Mantaux-Test (M.T)": 200, "Triple Antigen": 500, "HIV": 450, "HCV": 500, "TB (ICT)": 750, "Malaria. pf/pv": 700, "H. Pylori": 850, "Filaria (ICT)": 750, "Dengue NS1. IGG/IgM": 300,
    
    # --- HORMONE PANEL ---
    "T3": 1200, "T4": 1200, "FT3": 900, "FT4": 900, "TSH": 1100, "HbA1c": 1500, "Prolactin": 1200, "S. IgE": 1500, "S.IgE (Device Test)": 700,
    
    # --- BIO CHEMICAL ANALYSIS ---
    "Random Blood Sugar": 200, "Fasting Blood Sugar": 200, "2hr. After Breakfast (2HAB)": 200, "2hr. After 75gm Glucose": 200, "O.G.T.T": 500, "Blood Urea": 400, "Cholesterol": 350, "HDL": 400, "TG": 350, "LDL": 300, "S.GPT (ALT)": 500, "S.GOT (AST)": 500, "Bilirubin Total": 350, "Lipid Profile": 1000, "Bilirubin Direct/Indirect": 450, "Serum Creatinine": 400, "Uric Acid": 400, "Amylase": 700, "Calcium": 600,
    
    # --- X-RAY DIGITAL ---
    "X-Ray Chest": 500, "X-Ray PNS": 500, "X-Ray Maxilla": 500, "X-Ray Nasopharynx": 550, "X-Ray Abdomen A/P": 500, "X-Ray Cervical Spine": 600, "X-Ray Plane X-Ray Abdomen": 500, "X-Ray Mastoid Towns View": 500, "X-Ray Skull": 600, "X-Ray Pelvic": 500, "X-Ray Mandible B/V": 600, "X-Ray KUB": 500, "X-Ray D/S Spine": 600, "X-Ray L/S Spine": 600, "X-Ray Foot B/V": 500, "X-Ray Knee B/V": 550, "X-Ray Elbow B/V": 500, "X-Ray Shoulder Joint B/V": 550, "X-Ray Hip Joint": 500,
    
    # --- URINE, STOOL & ULTRASOUND ---
    "Urine Pregnancy Test (PT)": 200, "Urine R/E": 250, "Stool R/E": 400, "Stool OBT": 400, "USG Whole Abdomen": 1000, "USG Upper Abdomen": 800, "USG Lower Abdomen": 800, "USG KUB": 1000, "USG Pregnancy Profile": 800, "USG Breast": 1200, "USG Color Doppler": 2500
}

# ডাটাবেজ কানেকশন এবং নতুন referral_fee কলামসহ টেবিল তৈরি
conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bills
             (invoice_no TEXT PRIMARY KEY, date TEXT, patient TEXT, age TEXT, phone TEXT,
              doctor TEXT, total REAL, discount REAL, paid REAL, due REAL, referral_fee REAL)''')
conn.commit()

# ট্যাব তৈরি
tab1, tab2 = st.tabs(["📄 Billing / Cash Memo", "📊 Dashboard"])
with tab1:
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
    
    total_amount = 0.0
    test_rows = []
    for i, test in enumerate(selected_tests):
        price = test_directory[test]
        total_amount += price
        test_rows.append({"SL": i+1, "Test Name": test, "Rate (৳)": price})
    
    if selected_tests:
        st.dataframe(pd.DataFrame(test_rows), use_container_width=True)
    
    st.markdown('<div class="section-box-orange">💰 <b>Payment & Calculation (পেমেন্ট এবং হিসাব)</b></div>', unsafe_allow_html=True)
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        st.metric(label="Total Amount (মোট বিল):", value=f"৳ {total_amount:,.2f}")
    with col4:
        discount = st.number_input("Discount (ছাড় ৳):", min_value=0.0, step=10.0, value=0.0)
    with col5:
        net_total = max(0.0, total_amount - discount)
        paid = st.number_input("Paid Amount (জমা ৳):", min_value=0.0, max_value=net_total, step=50.0, value=net_total)
    with col6:
        due = max(0.0, net_total - paid)
        st.metric(label="Due Amount (বাকি বিল):", value=f"৳ {due:,.2f}")
            # বিল সেভ এবং রসিদ বাটন লজিক
    if st.button("Save Bill & Generate Invoice", key="save_bill_btn", type="primary"):
        if not patient_name:
            st.error("অনুগ্রহ করে রোগীর নাম লিখুন!")
        elif not selected_tests:
            st.error("অনুগ্রহ করে অন্তত একটি টেস্ট সিলেক্ট করুন!")
        else:
            invoice_no = f"INV-{int(datetime.now().timestamp())}"
            ref_fee = total_amount * 0.30  # ৩০% রেফারেল ফি অটোমেটিক হিসাব
            
            c.execute("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (invoice_no, date_today.strftime('%Y-%m-%d'), patient_name, age, phone, ref_dr, total_amount, discount, paid, due, ref_fee))
            conn.commit()
            st.success(f"বিল সফলভাবে সেভ হয়েছে! ইনভয়েস নম্বর: {invoice_no}")
            
            # --- রোগীর ক্যাশ মেমো বা রসিদ ভিউ (HTML ছক ডিজাইন) ---
            st.markdown("---")
            
            # রসিদের উপরের ছক ও হেডার
            html_header = f"""
            <div style="border: 2px solid #000000; padding: 20px; background-color: #ffffff; color: #000000; font-family: 'Courier New', Courier, monospace;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h1 style="color: #ff0000; margin: 0; font-size: 24px; font-weight: bold; letter-spacing: 1px;">ROGMUKTI DIAGNOSTIC CENTRE</h1>
                    <p style="margin: 5px 0 2px 0; font-size: 14px; font-weight: bold; color: #333333;">Mollah Market, Galachipa, Patuakhali</p>
                    <p style="margin: 0; font-size: 13px; font-weight: bold; color: #555555;">Mobile: 01646176947</p>
                    <div style="border-bottom: 2px double #000000; margin-top: 10px; margin-bottom: 5px;"></div>
                    <span style="background-color: #000000; color: #ffffff; padding: 3px 15px; font-size: 13px; font-weight: bold;">CASH MEMO / MONEY RECEIPT</span>
                </div>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 14px; color: #000000;">
                    <tr>
                        <td style="padding: 5px; width: 18%; font-weight: bold;">Invoice No:</td>
                        <td style="padding: 5px; width: 32%; border-bottom: 1px dotted #000;">{invoice_no}</td>
                        <td style="padding: 5px; width: 15%; font-weight: bold; text-align: right;">Date:</td>
                        <td style="padding: 5px; width: 35%; border-bottom: 1px dotted #000; text-align: center;">{date_today.strftime('%d-%m-%Y')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; font-weight: bold;">Patient Name:</td>
                        <td style="padding: 5px; border-bottom: 1px dotted #000; font-weight: bold;">{patient_name}</td>
                        <td style="padding: 5px; font-weight: bold; text-align: right;">Age/Sex:</td>
                        <td style="padding: 5px; border-bottom: 1px dotted #000; text-align: center;">{age}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; font-weight: bold;">Mobile No:</td>
                        <td style="padding: 5px; border-bottom: 1px dotted #000;">{phone}</td>
                        <td style="padding: 5px; font-weight: bold; text-align: right;">Ref. By:</td>
                        <td style="padding: 5px; border-bottom: 1px dotted #000; font-weight: bold; text-align: center;">{ref_dr}</td>
                    </tr>
                </table>
                <div style="border-bottom: 1px solid #000000; margin-bottom: 10px;"></div>
                <p style="margin: 0; font-weight: bold; font-size: 14px;">🔬 INVESTIGATION LIST (টেস্টের বিবরণ):</p>
            </div>
            """
            st.html(html_header)
            
            # টেস্ট টেবিল
            st.dataframe(pd.DataFrame(test_rows), use_container_width=True)
            
            # রসিদের নিচের মোট বিলের ছক ও বাটন
            html_footer = f"""
            <div style="border: 2px solid #000000; border-top: none; padding: 15px; background-color: #ffffff; color: #000000; font-family: 'Courier New', Courier, monospace;">
                <table style="width: 100%; font-size: 15px; font-weight: bold; border-collapse: collapse;">
                    <tr style="border-top: 1px solid #000; border-bottom: 1px solid #000;">
                        <td style="padding: 8px 5px; width: 25%;">Total Amount: ৳ {total_amount}</td>
                        <td style="padding: 8px 5px; width: 25%; color: blue;">Discount: ৳ {discount}</td>
                        <td style="padding: 8px 5px; width: 25%; color: green;">Paid Amount: ৳ {paid}</td>
                        <td style="padding: 8px 5px; width: 25%; color: red;">Due Amount: ৳ {due}</td>
                    </tr>
                </table>
                <div style="margin-top: 40px; display: flex; justify-content: space-between; font-size: 12px;">
                    <p style="border-top: 1px solid #000; width: 140px; text-align: center; margin: 0; color: #000000;">Prepared By</p>
                    <p style="border-top: 1px solid #000; width: 140px; text-align: center; margin: 0; color: #000000;">Authorized Signature</p>
                </div>
            </div>
            <br>
            """
            st.html(html_footer)
            
            # সবুজ প্রিন্ট বাটন
            st.markdown("""
                <button onclick="window.print()" style="background-color: #00E676; color: black; padding: 14px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%;">
                    🖨️ রোগীর এই রসিদটি (Cash Memo) প্রিন্ট করুন
                </button>
                <br><br>
            """, unsafe_allow_html=True)
            with tab2:
    st.header("📊 দৈনিক, সাপ্তাহিক ও মাসিক ড্যাশবোর্ড")
    df = pd.read_sql_query("SELECT * FROM bills", conn) if sqlite3.connect('rogmukti.db').cursor().execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bills'").fetchone() else pd.DataFrame()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        filter_option = st.selectbox("হিসাব দেখার সময় নির্বাচন করুন", ["সব সময়", "আজ", "এই সপ্তাহ", "এই মাস"], key="dashboard_time_filter_final")
        today = datetime.today()
        if filter_option == "আজ": filtered_df = df[df['date'].dt.date == today.date()]
        elif filter_option == "এই সপ্তাহ": filtered_df = df[df['date'] >= (today - timedelta(days=today.weekday()))]
        elif filter_option == "এই মাস": filtered_df = df[(df['date'].dt.month == today.month) & (df['date'].dt.year == today.year)]
        else: filtered_df = df
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("মোট কালেকশন", f"৳ {filtered_df['total'].sum() if 'total' in filtered_df else 0:,.2f}")
        c2.metric("মোট ডিসকাউন্ট", f"৳ {filtered_df['discount'].sum() if 'discount' in filtered_df else 0:,.2f}")
        c3.metric("মোট ডিউ (বাকি)", f"৳ {filtered_df['due'].sum() if 'due' in filtered_df else 0:,.2f}")
        c4.metric("মোট রেফারেল ফি (৩০%)", f"৳ {filtered_df['referral_fee'].sum() if 'referral_fee' in filtered_df else 0:,.2f}")
        st.subheader("👨‍⚕️ ডাক্তার ভিত্তিক রেফারেল রিপোর্ট (নামসহ)")
        available_cols = [col for col in ['doctor', 'patient', 'invoice_no', 'total', 'referral_fee', 'date'] if col in filtered_df]
        st.dataframe(filtered_df[available_cols], use_container_width=True)
        st.markdown('<button onclick="window.print()" style="background-color: #4CAF50; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold;">🖨️ এই ড্যাশবোর্ড রিপোর্টটি প্রিন্ট করুন</button>', unsafe_allow_html=True)
    else: st.info("ডেটাবেজে এখনো কোনো বিলের রেকর্ড নেই। একটি নতুন বিল সেভ করলেই ড্যাশবোর্ড সচল হয়ে যাবে।")
        
