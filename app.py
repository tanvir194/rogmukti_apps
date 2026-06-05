import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")
st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")

# ইনপুট বক্স, ড্রপডাউন এবং সিলেকশন বক্সের ভেতরের ঘরগুলো রঙিন করার CSS
st.markdown("""
    <style>
    /* ১. রোগী ও ডাক্তারের পুরো সেকশনের ব্যাকগ্রাউন্ড */
    .section-box-blue { background-color: #f1f8ff; padding: 12px; border-radius: 8px; border-left: 5px solid #1e88e5; margin-bottom: 15px; }
    /* ২. টেস্ট লিস্ট সেকশনের ব্যাকগ্রাউন্ড */
    .section-box-green { background-color: #f4faf6; padding: 12px; border-radius: 8px; border-left: 5px solid #43a047; margin-bottom: 15px; }
    /* ৩. পেমেন্ট সেকশনের ব্যাকগ্রাউন্ড */
    .section-box-orange { background-color: #fff9f0; padding: 12px; border-radius: 8px; border-left: 5px solid #fb8c00; margin-bottom: 15px; }
    
    /* ✍️ লেখার ও সিলেক্ট করার মূল ইনপুট ঘরগুলোর ভেতরের কালার স্টাইল */
    /* রোগীর নাম, বয়স, ফোন নাম্বার লেখার বক্সের ব্যাকগ্রাউন্ড হালকা নীল */
    .stTextInput input {
        background-color: #e3f2fd !important;
        border: 1px solid #1e88e5 !important;
        color: black !important;
        font-weight: bold !important;
    }
    /* ডাক্তার সিলেক্ট করার ড্রপডাউন বক্সের ব্যাকগ্রাউন্ড হালকা আকাশী */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #e0f7fa !important;
        border: 1px solid #00bcd4 !important;
        font-weight: bold !important;
    }
    /* পরীক্ষাগুলো সিলেক্ট করার মূল চয়েস বক্সের ব্যাকগ্রাউন্ড হালকা সবুজ */
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #e8f5e9 !important;
        border: 1px solid #43a047 !important;
        font-weight: bold !important;
    }
    /* ডিসকাউন্ট এবং জমার টাকা লেখার বক্সের ব্যাকগ্রাউন্ড হালকা হলুদ */
    .stNumberInput input {
        background-color: #fffde7 !important;
        border: 1px solid #fbc02d !important;
        color: black !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Bazar, Auliapur, Patuakhali<br>Phone: 01711-867637</p>", unsafe_allow_html=True)

doctors_list = ["Select Doctor", "Self / Direct", "Dr. Saiful Islam RMP", "DR. Abdur Rahman D M F", "DR. Moshiur Rahman MBBS BCS FCPS"]

test_directory = {
    "Select Test": 0,
    "(CBC) + ESR": 600, "CBC": 350, "ESR": 250, "Platelet Count": 300,
    "MP (Malaria Parasite)": 500, "BT/CT": 350, "Blood Group & Rh": 200,
    "Hemoglobin (Hb%)": 200, "PBF (Peripheral Blood Film)": 600,
    "Random Blood Sugar (RBS)": 200, "Fasting Blood Sugar (FBS)": 200, 
    "2 Hours After Breakfast (2HABF)": 200, "HbA1c": 1200,
    "Serum Creatinine": 400, "Serum Urea": 400, "Serum Uric Acid": 450,
    "Lipid Profile": 1000, "Serum Cholesterol": 300,
    "Serum Bilirubin (Jaundice)": 300, "SGPT (ALT)": 450, "SGOT (AST)": 450,
    "TSH": 800, "T3": 900, "T4": 900,
    "HBsAg": 400, "Widal Test (Typhoid)": 500, "CRP": 600, "Dengue NS1": 700,
    "Urine R/E": 250, "Urine Pregnancy Test": 300, "Stool R/E": 300,
    "USG of Whole Abdomen": 1000, "USG of Upper Abdomen": 800, 
    "USG of Lower Abdomen": 750, "USG of Pelvis": 700, "USG of KUB": 800,
    "X-Ray Chest P/A View": 500, "ECG": 400
}

conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bills
             (invoice_no TEXT PRIMARY KEY, date TEXT, patient TEXT, age TEXT, phone TEXT, 
              doctor TEXT, total REAL, discount REAL, paid REAL, due REAL)''')
conn.commit()

try:
    c.execute("ALTER TABLE bills ADD COLUMN due REAL DEFAULT 0")
    conn.commit()
except:
    pass

tab1, tab2 = st.tabs(["📑 Billing / Cash Memo", "📊 Dashboard"])

with tab1:
    st.markdown('<div class="section-box-blue">📢 <b>Patient Information & Doctor List (রোগী ও ডাক্তার তালিকা)</b></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name:")
        age = st.text_input("Age:")
        phone = st.text_input("Phone Number:")
    with col2:
        ref_dr = st.selectbox("Referred By:", doctors_list)
        date_today = st.date_input("Date:", datetime.now())

    st.divider()
    st.markdown('<div class="section-box-green">🧪 <b>Test Selection (টেস্ট লিস্ট)</b></div>', unsafe_allow_html=True)
    selected_tests = st.multiselect("পরীক্ষাগুলো সিলেক্ট করুন:", list(test_directory.keys())[1:])
    
    total_amount = 0
    test_list_html = ""
    
    if selected_tests:
        st.write("### 📋 নির্বাচিত টেস্টের তালিকা:")
        for idx, test in enumerate(selected_tests, 1):
            price = test_directory[test]
            st.write(f"{idx}. **{test}** — {price} TK")
            test_list_html += f"<tr><td style='padding:8px; border:1px solid #ddd;'>{idx}</td><td style='padding:8px; border:1px solid #ddd;'>{test}</td><td style='padding:8px; border:1px solid #ddd; text-align:right;'>{price} TK</td></tr>"
            total_amount += price

    st.divider()
    st.markdown('<div class="section-box-orange">💰 <b>Payment Details (বিল ও জমা)</b></div>', unsafe_allow_html=True)
    
    test_list_html = ""
    
    if selected_tests:
        st.write("### 📋 নির্বাচিত টেস্টের তালিকা:")
        for idx, test in enumerate(selected_tests, 1):
            price = test_directory[test]
            st.write(f"{idx}. **{test}** — {price} TK")
            test_list_html += f"<tr><td style='padding:8px; border:1px solid #ddd;'>{idx}</td><td style='padding:8px; border:1px solid #ddd;'>{test}</td><td style='padding:8px; border:1px solid #ddd; text-align:right;'>{price} TK</td></tr>"
            total_amount += price

    st.divider()
    # ৪. পেমেন্ট সেকশনে অরেঞ্জ কালার বক্স
    st.markdown('<div class="section-box-orange">💰 <b>Payment Details (বিল ও জমা)</b></div>', unsafe_allow_html=True)
    
    c_dis, c_paid = st.columns(2)
    with c_dis:
        discount = st.number_input("Discount (TK)", min_value=0, value=0, step=10)
    with c_paid:
        net_payable = total_amount - discount
        paid_amount = st.number_input("Paid Amount (জমা)", min_value=0, value=int(net_payable), step=50)
    
    due_amount = net_payable - paid_amount
    
    col_t1, col_t2, col_t3 = st.columns(3)
    col_t1.markdown(f"**Total Amount:** {total_amount} TK")
    col_t2.markdown(f"**Discount:** {discount} TK")
    if due_amount > 0:
        col_t3.markdown(f"### <span style='color:red;'>Due Amount (বাকি): {due_amount} TK</span>", unsafe_allow_html=True)
    else:
        col_t3.markdown(f"### <span style='color:green;'>Paid (পরিশোধিত)</span>", unsafe_allow_html=True)

    if st.button("💾 Save & Generate Invoice", type="primary"):
        if patient_name and ref_dr != "Select Doctor" and selected_tests:
            today_str = datetime.now().strftime("%Y%m%d")
                        # টাপল (Tuple) থেকে সংখ্যা আলাদা করার সঠিক কোড
            c.execute("SELECT COUNT(*) FROM bills")
            count_result = c.fetchone()[0]
            invoice_no = f"ROG-{today_str}-{(count_result + 1):03d}"
            
            c.execute("""INSERT OR REPLACE INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (invoice_no, str(date_today), patient_name, age, phone, ref_dr, total_amount, discount, paid_amount, due_amount))
                        # প্রিন্ট দেওয়ার সময় ক্যাশ মেমোর বাইরের সবকিছু লুকিয়ে ফেলার বিশেষ স্টাইলসহ HTML
            memo_html = f"""
            <html>
            <head>
                <style>
                    @media print {{
                        body * {{
                            visibility: hidden;
                        }}
                        #print-memo-area, #print-memo-area * {{
                            visibility: visible;
                        }}
                        #print-memo-area {{
                            position: absolute;
                            left: 0;
                            top: 0;
