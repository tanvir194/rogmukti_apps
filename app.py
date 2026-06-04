import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="centered")

st.markdown("<h1 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Bazar, Auliapur, Patuakhali<br>Phone: 01711-867637</p>", unsafe_allow_html=True)

doctors_list = ["Select Doctor", "Self / Direct", "Dr. Saiful Islam RMP", "DR. Abdur Rahman D M F", "DR. Moshiur Rahman MBBS BCS FCPS"]

test_directory = {
    "Select Test": 0,
    "(CBC) + ESR": 600, "CBC (Complete Blood Count)": 350, "ESR": 150, "Platelet Count": 250,
    "Hemoglobin (Hb%)": 150, "Blood Group & Rh Factor": 150, "BT / CT (Bleeding & Clotting Time)": 200,
    "MP (Malarial Parasite)": 250, "ASO Titre": 400, "RA Test": 400, "CRP (C-Reactive Protein)": 500,
    "Random Blood Sugar (RBS)": 150, "Fasting Blood Sugar (FBS)": 150, "2 Hours After Breakfast (2HABF)": 150,
    "HbA1c": 1200, "Serum Creatinine": 300, "Serum Urea": 300, "Serum Uric Acid": 350,
    "Serum Bilirubin (Total)": 250, "SGPT (ALT)": 350, "SGOT (AST)": 350, "Serum Alkaline Phosphatase": 350,
    "Lipid Profile": 900, "Serum Cholesterol": 250, "Serum Triglycerides (TG)": 300,
    "Serum Calcium": 450, "Serum Electrolytes": 1000,
    "HBsAg (Screening)": 300, "HBsAg (ELISA)": 600, "Anti HCV": 600, "HIV I & II": 500,
    "VDRL (Qualitative)": 250, "TPHA": 400, "Widal Test (Typhoid)": 350, "Dengue NS1 Antigen": 600,
    "Dengue IgG / IgM": 600, "Chikungunya IgM": 800, "Troponin-I": 1200,
    "Serum T3": 600, "Serum T4": 600, "Serum TSH": 700, "FT3 (Free T3)": 700, "FT4 (Free T4)": 700,
    "Serum Prolactin": 800, "Serum Testosterone": 1000, "Beta hCG (Pregnancy)": 900,
    "Urine R/E (Routine & Examination)": 200, "Urine Pregnancy Test (UPT)": 150,
    "Stool R/E": 200, "Stool for OBT (Occult Blood Test)": 250,
    "USG of Whole Abdomen": 800, "USG of Upper Abdomen": 500, "USG of Lower Abdomen": 500,
    "USG of Pregnancy / Obs": 500, "USG of Pelvis": 500, "USG of KUB (Kidney, Ureter, Bladder)": 600,
    "USG of KUB with Prostate": 700,
    "X-Ray Chest P/A View": 400, "X-Ray Chest A/P View": 400, "X-Ray Lumbar Spine B/V": 700,
    "X-Ray Cervical Spine B/V": 600, "ECG (Digital)": 300
}

conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bills
             (invoice_no TEXT PRIMARY KEY, date TEXT, patient TEXT, age TEXT, phone TEXT, 
              doctor TEXT, total REAL, discount REAL, paid REAL)''')
conn.commit()

if 'sales_data' not in st.session_state:
    st.session_state['sales_data'] = pd.DataFrame(columns=["Invoice_No", "Date", "Patient", "Age", "Phone", "Doctor", "Total", "Discount", "Paid"])

if 'show_memo' not in st.session_state:
    st.session_state['show_memo'] = False
    st.session_state['last_memo_html'] = ""

if 'num_tests' not in st.session_state:
    st.session_state['num_tests'] = 3

tab1, tab2 = st.tabs(["📑 Billing / Cash Memo", "📊 Dashboard"])

with tab1:
    st.subheader("Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name:", key="p_name")
        age = st.text_input("Age:", key="p_age")
        phone = st.text_input("Phone Number:", key="p_phone")
    with col2:
        ref_dr = st.selectbox("Referred By:", doctors_list, key="p_dr")
        date_today = st.date_input("Date:", datetime.now().date(), key="p_date")

    st.divider()
    st.subheader("🧪 Test Selection")
    
    total_amount = 0
    test_list_html = ""
    serial = 1
    
    for i in range(1, st.session_state['num_tests'] + 1):
        test = st.selectbox(f"Test {i}:", list(test_directory.keys()), key=f"dynamic_test_{i}")
        if test != "Select Test":
            price = test_directory[test]
            st.write(f"✅ {test} = **{price} TK**")
            test_list_html += f"<tr><td style='padding:8px; border-bottom:1px solid #eee;'>{serial}</td><td style='padding:8px; border-bottom:1px solid #eee;'>{test}</td><td style='padding:8px; border-bottom:1px solid #eee; text-align:right;'>{price} TK</td></tr>"
            total_amount += price
            serial += 1

    if st.button("➕ Add More Test Slot"):
        st.session_state['num_tests'] += 1
        st.rerun()

    st.divider()
    discount = st.number_input("Discount (TK)", min_value=0, value=0, step=10, key="p_discount")
    total_paid = total_amount - discount

    st.markdown(f"**Total Amount:** {total_amount} TK")
    st.markdown(f"**Discount:** {discount} TK")
    st.markdown(f"### **Net Payable:** {total_paid} TK")

    if st.button("💾 Save & Print Invoice", type="primary"):
        if patient_name and ref_dr != "Select Doctor" and total_amount > 0:
            today_str = datetime.now().strftime("%Y%m%d")
            invoice_no = f"ROG-{today_str}-{len(st.session_state['sales_data'])+1:03d}"
            
            new_row = {
                "Invoice_No": invoice_no,
                "Date": str(date_today),
                "Patient": patient_name,
                "Age": age,
                "Phone": phone,
                "Doctor": ref_dr,
                "Total": total_amount,
                "Discount": discount,
                "Paid": total_paid
            }
            
            c.execute("""INSERT OR REPLACE INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (invoice_no, str(date_today), patient_name, age, phone, ref_dr, total_amount, discount, total_paid))
            conn.commit()
            
            st.session_state['sales_data'] = pd.concat([st.session_state['sales_data'], pd.DataFrame([new_row])], ignore_index=True)
            
            memo_html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 30px; border: 3px solid black; background: white; color: black;">
                <h2 style="text-align: center; color: red; margin-bottom: 5px;">ROGMUKTI DIAGNOSTIC CENTRE</h2>
                <p style="text-align: center; margin-top: 0; font-size: 14px;">Mollah Bazar, Auliapur, Patuakhali | 01711-867637</p>
                <p style="text-align: center; font-size: 12px; font-weight: bold; margin: 10px 0;">Invoice No: {invoice_no}</p>
                <hr style="border: 1px solid black;">
                <table style="width:100%; font-size:14px; margin-bottom: 10px;">
                    <tr><td><b>Patient Name:</b> {patient_name}</td><td style="text-align:right;"><b>Date:</b> {date_today}</td></tr>
                    <tr><td><b>Age / Phone:</b> {age} / {phone}</td><td style="text-align:right;"><b>Ref. By:</b> {ref_dr}</td></tr>
                </table>
                <table style="width:100%; border-collapse:collapse; font-size:14px; margin-top: 15px;">
                    <tr style="background:#f0f0f0; font-weight:bold; border-top: 2px solid black; border-bottom: 2px solid black;">
                        <td style="padding:8px; width:40px;">Sl.</td>
                        <td style="padding:8px;">Test Name</td>
                        <td style="padding:8px; text-align:right;">Price</td>
                    </tr>
                    {test_list_html}
                </table>
                <hr style="border-top: 1px dashed black; margin-top: 20px;">
                <table style="width:100%; font-weight:bold; font-size:15px; line-height: 1.6;">
                    <tr><td style="text-align:right; width:70%;">Total Amount:</td><td style="text-align:right;">{total_amount} TK</td></tr>
                    <tr><td style="text-align:right; color:red;">Discount:</td><td style="text-align:right; color:red;">{discount} TK</td></tr>
                    <tr style="font-size:17px; color:green; border-top: 1px solid black;"><td style="text-align:right;">Net Payable:</td><td style="text-align:right;">{total_paid} TK</td></tr>
                </table>
                <p style="text-align:center; margin-top:40px; font-style: italic; font-size: 13px;">Thank You for choosing us!</p>
            </div>
            """
            st.session_state['last_memo_html'] = memo_html
            st.session_state['show_memo'] = True
            st.session_state['num_tests'] = 3
            st.success(f"✅ Invoice Saved! Invoice No: **{invoice_no}**")
            st.rerun()
            
        else:
            st.error("অনুগ্রহ করে Patient Name, Doctor সিলেক্ট করুন এবং অন্তত ১টি টেস্ট যুক্ত করুন।")

    if st.session_state['show_memo']:
        st.divider()
        st.subheader("🖨️ Last Generated Invoice Print View")
        st.components.v1.html(st.session_state['last_memo_html'], height=520, scrolling=True)
        st.markdown('<button onclick="window.print()" style="background:#28a745;color:white;padding:15px 30px;font-size:19px;border:none;border-radius:5px;width:100%;margin-top:15px;font-weight:bold;">🖨️ Print / Save Memo as PDF</button>', unsafe_allow_html=True)
        if st.button("🧹 Clear Memo Preview"):
            st.session_state['show_memo'] = False
            st.rerun()

with tab2:
    st.header("🔒 Admin Dashboard Lock")
    input_password = st.text_input("এডমিন পাসওয়ার্ড দিন:", type="password", key="admin_password_input")
    
    if input_password != "rogmukti123":
        if input_password != "":
            st.error("❌ ভুল পাসওয়ার্ড! অনুগ্রহ করে সঠিক পাসওয়ার্ড দিন।")
        st.stop()

    st.success("🔓 এক্সেস গ্র্যান্টেড! ড্যাশবোর্ড ওপেন হয়েছে।")
    st.divider()
    
    df_db = pd.read_sql_query("SELECT * FROM bills", conn)
    
    if not df_db.empty:
        df_db['Date'] = pd.to_datetime(df_db['date']).dt.date
        cols_mapping = {'invoice_no': 'Invoice_No', 'patient': 'Patient', 'age': 'Age', 'phone': 'Phone', 'doctor': 'Doctor', 'total': 'Total', 'discount': 'Discount', 'paid': 'Paid'}
        df = df_db.rename(columns=cols_mapping)
    else:
