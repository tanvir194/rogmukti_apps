import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Rog Mukti Diagnostic Centre",
    page_icon="🏥",
    layout="wide"
)
st.markdown("""
<style>
    .metric-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        text-align: center;
        border-left: 5px solid #007bff;
    }
    .metric-title { font-size: 16px; color: #6c757d; font-weight: bold; }
    .metric-value { font-size: 24px; color: #1c3d5a; font-weight: bold; margin-top: 5px; }
    .receipt-box {
        border: 2px solid #1c3d5a;
        padding: 20px;
        border-radius: 8px;
        background-color: #ffffff;
        max-width: 600px;
        margin: auto;
        font-family: 'Arial', sans-serif;
    }
    .receipt-header {
        background-color: #0b5394;
        color: white;
        text-align: center;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    .receipt-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
    }
    .receipt-table th {
        background-color: #3d85c6;
        color: white;
        padding: 8px;
        text-align: left;
    }
    .receipt-table td {
        border-bottom: 1px solid #dddddd;
        padding: 8px;
    }
</style>
""", unsafe_allow_html=True)
# Database Connection Setup
conn = sqlite3.connect("rogmukti_clinic_final.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    phone TEXT,
    doctor TEXT,
    tests TEXT,
    total_amount REAL,
    discount REAL,
    advance REAL,
    due REAL,
    date TEXT
)
""")
conn.commit()

def add_patient(name, age, phone, doctor, tests, total, discount, advance, due, date_str):
    c.execute("""
    INSERT INTO patients (name, age, phone, doctor, tests, total_amount, discount, advance, due, date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, age, phone, doctor, tests, total, discount, advance, due, date_str))
    conn.commit()
    return c.lastrowid
    TEST_PRICES = {
    "Amylase": 700.0, "Bilirubin Direct/Indirect": 450.0, "Blood Group & Rh Factor": 200.0,
    "C/E Count": 250.0, "BT/CT (Bleeding & Clotting Time)": 350.0, "Aso Titre": 450.0,
    "CBC (Complete Blood Count)": 500.0, "CBC with ESR": 600.0, "TC.DC.": 250.0,
    "Hb% (Hemoglobin)": 350.0, "ESR": 200.0, "Platelet Count": 300.0,
    "MP (Malaria Parasite)": 500.0, "Widal Test": 450.0, "CRP": 450.0,
    "RA/RF": 450.0, "HBsAg (Screen Test)": 450.0, "TPHA": 450.0, "VDRL": 400.0,
    "Mantoux-Test (M.T.)": 200.0, "Triple Antigen": 1050.0, "F.Widal": 400.0,
    "HIV I & II": 450.0, "HCV": 500.0, "TB (ICT)": 750.0, "Malaria pf/pv": 700.0,
    "H. Pylori": 850.0, "Febrile Antigen / Fallaria (ICT)": 750.0, "Dengue NS1": 500.0,
    "IgE (Screen Test)": 750.0, "Dengue (IgG/IgM)": 500.0, "X-Ray Chest": 500.0, "X-Ray PNS": 500.0
}

DOCTOR_LIST = [
    "Dr. MD. MOSHIUR RAHMAN MBBS BCS PGT RMO - PATUAKHALI HOSPITAL",
    "Self / None"
]

st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", ["New Patient Entry", "Patient Database", "Doctors Report"])
if page == "New Patient Entry":
    st.title("🏥 Rog Mukti Diagnostic Centre")
    st.subheader("👤 Patient & Doctor Information")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name of the PT *", value="Demo")
        age = st.number_input("Age (Years)", min_value=0, max_value=120, value=25)
        phone = st.text_input("Phone Number", value="Demo")
    with col2:
        doctor = st.selectbox("REFd By: Dr.", DOCTOR_LIST)
        current_date = st.date_input("Date", datetime.now())
    
    st.subheader("🧪 Tests & Billing Selection")
    selected_tests = st.multiselect("Description (Search or select tests)", list(TEST_PRICES.keys()), 
                                    default=["Amylase", "Bilirubin Direct/Indirect", "Blood Group & Rh Factor", "C/E Count", "BT/CT (Bleeding & Clotting Time)", "Aso Titre"])
    
    subtotal = sum(TEST_PRICES[test] for test in selected_tests)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"### 📊 Live Total Fee: **{subtotal:.2f} TK**")
        discount_pct = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
        advance = st.number_input("Advance Paid (TK)", min_value=0.0, value=1920.0, step=10.0)
    
    discount_amount = (subtotal * discount_pct) / 100
    total_payable = subtotal - discount_amount
    due = total_payable - advance
    
    with col4:
        st.write(f"**Discount Amount:** {discount_amount:.2f} TK")
        st.markdown("### 🔴 Due (Total Remaining Balance):")
        st.markdown(f"## **{due:.2f} TK**")
            if 'show_receipt' not in st.session_state:
        st.session_state.show_receipt = False
        st.session_state.inv_id = 0

    if st.button("💾 Save Bill and Generate Receipt", type="primary"):
        if name:
            date_str = current_date.strftime("%Y-%m-%d")
            tests_str = ", ".join(selected_tests)
            st.session_state.inv_id = add_patient(name, age, phone, doctor, tests_str, total_payable, discount_amount, advance, due, date_str)
            st.session_state.show_receipt = True
            st.success("Data saved successfully! Print menu and Invoice are available below.")
        else:
            st.error("Please enter the Patient's Name.")

    if st.session_state.show_receipt:
        st.subheader("🖨️ Receipt Action Menu")
        st.button("📠 Print Receipt Now")
        
        receipt_html = f"""
        <div class="receipt-box">
            <div class="receipt-header">
                <h2>Rog Mukti Diagnostic Centre</h2>
                <p>Motlob Stand, Auliapur, Patuakhali<br>Phone: 01711867637</p>
                <div style="background-color:white; color:black; display:inline-block; padding:2px 10px; font-weight:bold; border-radius:4px;">MONEY RECEIPT</div>
            </div>
            <table style="width:100%; font-size:14px; margin-bottom:15px;">
                <tr><td><b>Invoice No:</b> {st.session_state.inv_id:05d}</td><td style="text-align:right;"><b>Date:</b> {current_date.strftime('%Y-%m-%d')}</td></tr>
                <tr><td><b>Patient Name:</b> {name}</td><td style="text-align:right;"><b>Age:</b> {age} Years</td></tr>
                <tr><td><b>Phone Number:</b> {phone}</td><td style="text-align:right;"><b>Refd By:</b> {doctor}</td></tr>
            </table>
            <table class="receipt-table">
                <tr><th>SL</th><th>Description</th><th style="text-align:right;">Amount</th></tr>
        """
        idx = 1
        for test in selected_tests:
            test_fee = TEST_PRICES[test]
            receipt_html = receipt_html + f"<tr><td>{idx}</td><td>{test}</td><td style="text-align:right;">{test_fee:.2f} ৳</td></tr>"
            idx = idx + 1
            
        receipt_html = receipt_html + f"""
                <tr><td colspan="2" style="text-align:right; font-weight:bold;">Total Amount:</td><td style="text-align:right; font-weight:bold;">{subtotal:.2f} ৳</td></tr>
                <tr><td colspan="2" style="text-align:right; color:green;">Discount ({discount_pct}%):</td><td style="text-align:right; color:green;">-{discount_amount:.2f} ৳</td></tr>
                <tr><td colspan="2" style="text-align:right; font-weight:bold;">Advance Paid:</td><td style="text-align:right; font-weight:bold;">{advance:.2f} ৳</td></tr>
                <tr style="background-color:#fce4d6;"><td colspan="2" style="text-align:right; font-weight:bold; color:#c00000;">Due Amount:</td><td style="text-align:right; font-weight:bold; color:#c00000;">{due:.2f} ৳</td></tr>
            </table>
        </div>
        """
        st.markdown(receipt_html, unsafe_allow_html=True)
        elif page == "Patient Database":
    st.title("📋 Patient Record Database")
    st.markdown("---")
    st.markdown("#### 🔍 Filter Options")
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        start_date = st.date_input("Start Date", datetime.now())
    with f_col2:
        end_date = st.date_input("End Date", datetime.now())
    with f_col3:
        search_name = st.text_input("Search by Patient Name")
        
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    query = "SELECT id, name, age, phone, doctor, tests, total_amount, discount, advance, due, date FROM patients WHERE date(date) BETWEEN date(?) AND date(?)"
    params = [start_str, end_str]
    
    if search_name:
        query += " AND name LIKE ?"
        params.append(f"%{search_name}%")
    query += " ORDER BY id DESC"
    
    c.execute(query, params)
    rows = c.fetchall()
    
    if rows:
        df = pd.DataFrame(rows, columns=["INV ID", "Patient Name", "Age", "Phone Number", "Referred Doctor", "Tests", "Total Bill", "Discount", "Paid", "Due", "Date"])
        df["INV ID"] = df["INV ID"].apply(lambda x: f"{x:05d}")
        
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.markdown(f'<div class="metric-box"><div class="metric-title">Total Registered</div><div class="metric-value">{len(df)} Patients</div></div>', unsafe_allow_html=True)
        with s_col2:
            st.markdown(f'<div class="metric-box"><div class="metric-title">Total Collected</div><div class="metric-value">{df["Paid"].sum():.2f} TK</div></div>', unsafe_allow_html=True)
        with s_col3:
            st.markdown(f'<div class="metric-box" style="border-left-color: #dc3545;"><div class="metric-title">Total Due</div><div class="metric-value" style="color: #dc3545;">{df["Due"].sum():.2f} TK</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Database Report (CSV)", data=csv, file_name=f"patient_database_{start_str}.csv", mime="text/csv")
    else:
        st.info("No records found. Try changing the start date to yesterday.")
        elif page == "Doctors Report":
    st.title("📊 Doctors Referral & Collection Dashboard")
    st.markdown("---")
    st.markdown("#### 📅 Select Timeline & Doctor")
    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1:
        d_start_date = st.date_input("Start Date ", datetime.now())
    with d_col2:
        d_end_date = st.date_input("End Date ", datetime.now())
    with d_col3:
        filter_doc = st.selectbox("Filter by Doctor Name", ["All Doctors"] + DOCTOR_LIST)
        
    d_start_str = d_start_date.strftime("%Y-%m-%d")
    d_end_str = d_end_date.strftime("%Y-%m-%d")
    
    query = "SELECT total_amount, doctor, name, id, due, advance, date FROM patients WHERE date(date) BETWEEN date(?) AND date(?)"
    params = [d_start_str, d_end_str]
    
    if filter_doc != "All Doctors":
        query += " AND doctor = ?"
        params.append(filter_doc)
        
    c.execute(query, params)
    rows = c.fetchall()
    
    if rows:
        report_df = pd.DataFrame(rows, columns=["Total Value", "Doctor Name", "Patient Name", "Invoice ID", "Due", "Paid", "Date"])
        report_df["Invoice ID"] = report_df["Invoice ID"].apply(lambda x: f"{x:05d}")
        
        total_volume = report_df["Total Value"].sum()
        total_commission = total_volume * 0.10 
        total_received = report_df["Paid"].sum()
        
        st.subheader("📊 Doctors Summary")
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f'<div class="metric-box"><div class="metric-title">Total Business Volume</div><div class="metric-value">{total_volume:.2f} TK</div></div>', unsafe_allow_html=True)
        with m_col2:
            st.markdown(f'<div class="metric-box" style="border-left-color: #28a745;"><div class="metric-title">Total Referral Commission (10%)</div><div class="metric-value" style="color: #28a745;">{total_commission:.2f} TK</div></div>', unsafe_allow_html=True)
        with m_col3:
            st.markdown(f'<div class="metric-box"><div class="metric-title">Net Direct Cash Inflow</div><div class="metric-value">{total_received:.2f} TK</div></div>', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📋 Patient Lists under Selected Range")
        st.dataframe(report_df[["Invoice ID", "Patient Name", "Doctor Name", "Total Value", "Paid", "Due", "Date"]], use_container_width=True)
        
        csv_doc = report_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Doctor's Statement", data=csv_doc, file_name=f"doctor_report_{d_start_str}.csv", mime="text/csv")
    else:
        st.info("No transaction logs found for this timeline or filter setup.")
        
