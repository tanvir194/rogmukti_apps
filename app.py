import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Rog Mukti Diagnostic Centre", 
    layout="wide"
)
# Database Connection Setup
conn = sqlite3.connect("rogmukti_clinic_final.db", check_same_thread=False)
c = conn.cursor()

# Create Patients Table Structure
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

# Function to Insert Patient Record
def add_patient(name, age, phone, doctor, tests, total, discount, advance, due, date):
    c.execute('''
        INSERT INTO patients (name, age, phone, doctor, tests, total_amount, discount, advance, due, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, phone, doctor, tests, total, discount, advance, due, date))
    conn.commit()
    return c.lastrowid
# Master Price List Dictionary
TEST_PRICES = {
    # --- Haematology & Blood ---
    "CBC (Complete Blood Count)": 600.0,
    "Hgb (Hemoglobin)": 150.0,
    "ESR (Erythrocyte Sedimentation Rate)": 150.0,
    "WBC Count & DC": 250.0,
    "Platelet Count": 200.0,
    "Blood Grouping & Rh Typing": 250.0,
    "BT & CT (Bleeding & Clotting Time)": 200.0,
    "PBF (Peripheral Blood Film)": 450.0,
    "Malaria Parasite (MP)": 500.0,
    
    # --- Biochemistry & Diabetes ---
    "Blood Sugar (RBS / Fasting / 2H HAB)": 200.0,
    "HbA1c": 1200.0,
    "Serum Creatinine": 400.0,
    "Serum Bilirubin (Total/Direct)": 550.0,
    "SGPT (ALT)": 450.0,
    "SGOT (AST)": 450.0,
    "Serum Alkaline Phosphatase": 450.0,
    "Lipid Profile (Full)": 1000.0,
    "Serum Cholesterol": 250.0,
    "Serum Triglycerides": 450.0,
    "Serum Uric Acid": 450.0,
    "Serum Urea / BUN": 400.0,
    "Serum Electrolytes (Na, K, Cl)": 1000.0,
    "Serum Calcium": 700.0,
    
    # --- Serology & Immunology ---
    "HBsAg (Screening / ELISA)": 450.0,
    "Anti-HCV": 600.0,
    "HIV I & II": 500.0,
    "Widal Test (Typhoid)": 450.0,
    "ASO Titre": 400.0,
    "RA Factor": 400.0,
    "CRP (C-Reactive Protein)": 500.0,
    "Dengue NS1 Antigen": 300.0,
    "Dengue IgG/IgM": 300.0,
    "Chikungunya IgM": 800.0,
    "Troponin I (Cardiac)": 1200.0,
    "triple antigen Test (T.A)": 850.0,
    
    # --- Urine & Stool ---
    "Urine R/M/E": 200.0,
    "Urine Pregnancy Test (HCG)": 200.0,
    "Stool R/M/E": 200.0,
    "Stool for Occult Blood Test (OBT)": 250.0,
    
    # --- Thyroid & Hormone Panel ---
    "TSH (Thyroid Stimulating Hormone)": 900.0,
    "FT4 (Free Thyroxine)": 900.0,
    "FT3 (Free Triiodothyronine)": 900.0,
    "T3 (Total Triiodothyronine)": 900.0,
    "T4 (Total Thyroxine)": 900.0,
    "Serum Prolactin": 1200.0,
    "Serum Testosterone": 900.0,
    "PSA (Prostate Specific Antigen)": 1200.0,
    "Beta-HCG": 1000.0,
    
    # --- Vitamin & Tumor Markers ---
    "Vitamin D3 (25-OH Vitamin D)": 2500.0,
    "Vitamin B12": 1500.0,
    "Serum Ferritin": 1000.0,
    "CEA (Carcinoembryonic Antigen)": 1200.0,
    "CA-125 (Ovarian Marker)": 1500.0,
    "AFP (Alpha Fetoprotein)": 1200.0,
    
    # --- Imaging & Cardiology ---
    "ECG (Electrocardiogram)": 400.0,
    "ETT (Exercise Tolerance Test)": 3000.0,
    "Echocardiography (2D & Color Doppler)": 2000.0,
    "USG of Whole Abdomen": 1500.0,
    "USG of Pregnancy / Obstetric": 800.0,
    "USG of Lower Abdomen": 1000.0,
    "USG of Upper Abdomen": 1000.0,
    "USG of Thyroid Gland / KUB": 1200.0,
    "USG of Breast (Bilateral)": 1800.0,
    "X-Ray Chest P/A View (Digital)": 500.0,
    "X-Ray Lumbar Spine A/P & Lat": 800.0,
    "X-Ray Cervical Spine A/P & Lat": 800.0,
    "X-Ray KUB View": 500.0,
    
    # --- Custom Test Option ---
    "Custom Test / Others (Type Name & Price Below)": 0.0
}
# Sidebar Navigation Menu Options
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", ["New Patient Entry", "Patient Database", "Doctors Report"])

if page == "New Patient Entry":
    st.title("🏥 Rog Mukti Diagnostic Centre")
    st.markdown("---")
    
    if "receipt_data" not in st.session_state:
        st.session_state.receipt_data = None

    # Patient Demographic Fields
    st.subheader("👤 Patient & Doctor Information")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name of the PT *")
        age = st.number_input("Age (Years)", min_value=0, max_value=120, value=25)
        phone = st.text_input("Phone Number")
    with col2:
        doctor_list = ["Dr. Saidul Islam", "Dr. Nasrin Sultana", "Dr. Motaleb Hossain", "Self / Others"]
        doctor = st.selectbox("REFd By. Dr", doctor_list)
        date_input = st.date_input("Date", datetime.now())
        date_str = date_input.strftime("%Y-%m-%d")
    st.markdown("---")
    st.subheader("🧪 Tests & Billing Selection")
    
    # Form-independent dropdown for live counter updates
    selected_tests = st.multiselect("Description (Search or select tests)", sorted(list(TEST_PRICES.keys())))
    
    custom_test_active = "Custom Test / Others (Type Name & Price Below)" in selected_tests
    custom_name = ""
    custom_price = 0.0
    
    if custom_test_active:
        st.info("💡 Custom Test is active. Please enter name and price below.")
        
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if custom_test_active:
            custom_name = st.text_input("Enter Custom Test Name:")
    with col_c2:
        if custom_test_active:
            custom_price = st.number_input("Enter Custom Test Price (TK):", min_value=0.0, value=0.0, step=50.0)
    
    # Live billing math
    sub_total = sum(TEST_PRICES[test] for test in selected_tests) + custom_price

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"### 🧮 Live Total Fee: `{sub_total}` TK")
        discount_pct = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        advance = st.number_input("Advance Paid (TK)", min_value=0.0, value=0.0, step=50.0)
    with col4:
        discount_amount = sub_total * (discount_pct / 100)
        due = sub_total - (discount_amount + advance)
        st.write(f"**Discount Amount:** {discount_amount} TK")
        st.metric(label="Due (Total Remaining Balance)", value=f"{due} TK")

    st.markdown("---")
    
    # Save button trigger
    if st.button("💾 Save Bill and Generate Receipt", type="primary", use_container_width=True):
        if name and selected_tests:
            final_tests_list = [t for t in selected_tests if t != "Custom Test / Others (Type Name & Price Below)"]
            if custom_test_active and custom_name:
                final_tests_list.append(f"{custom_name} (Custom)")
            
            tests_str = ", ".join(final_tests_list)
            invoice_id = add_patient(name, age, phone, doctor, tests_str, sub_total, discount_pct, advance, due, date_str)
            
            receipt_tests = []
            for test in selected_tests:
                if test == "Custom Test / Others (Type Name & Price Below)":
                    if custom_name:
                        receipt_tests.append({"name": custom_name, "price": custom_price})
                else:
                    receipt_tests.append({"name": test, "price": TEST_PRICES[test]})

            st.session_state.receipt_data = {
                "inv_no": f"{invoice_id:05d}",
                "date": date_str,
                "name": name,
                "age": age,
                "doctor": doctor,
                "phone": phone,
                "tests": receipt_tests,
                "total": sub_total,
                "discount_pct": discount_pct,
                "discount_amt": discount_amount,
                "advance": advance,
                "due": due
            }
            st.success("Data saved successfully! Print menu and invoice are available below.")
        elif not name:
            st.error("Please enter the Patient's Name.")
        elif not selected_tests:
            st.error("Please select at least one test.")
    # Receipt View Generator & Native 1-Click Browser Print Trigger
    if st.session_state.receipt_data:
        r = st.session_state.receipt_data
        table_rows = ""
        for i, item in enumerate(r['tests'], 1):
            table_rows += f"<tr><td>{i}</td><td>{item['name']}</td><td style='text-align:right;'>{item['price']:.2f} ৳</td></tr>"

        html_receipt = f"""
        <div style="border: 3px solid #1e3a8a; padding: 25px; border-radius: 12px; background-color: #f8fafc; font-family: sans-serif; max-width: 650px; margin: 0 auto;">
            <div style="text-align: center; background-color: #1e3a8a; color: white; padding: 15px; border-radius: 8px 8px 0 0; margin: -25px -25px 20px -25px;">
                <h2 style="margin: 0; font-size: 24px;">Rog Mukti Diagnostic Centre</h2>
                <p style="margin: 5px 0 0 0; font-size: 13px;">Mollah Stand, Auliapur, Patuakhali</p>
                <p style="margin: 2px 0 0 0; font-size: 13px; font-weight: bold;">📞 Phone: 01711867637</p>
            </div>
            <div style="text-align: center; margin-bottom: 15px;"><span style="background-color: #e2e8f0; padding: 5px 18px; font-weight: bold; border-radius: 20px; color: #0f172a; font-size: 14px;">MONEY RECEIPT</span></div>
            <table style="width: 100%; font-size: 13px; margin-bottom: 15px; background: white; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <tr><td><b>Invoice No:</b> {r['inv_no']}</td><td style="text-align: right;"><b>Date:</b> {r['date']}</td></tr>
                <tr><td><b>Patient Name:</b> {r['name']}</td><td style="text-align: right;"><b>Age:</b> {r['age']} Years</td></tr>
                <tr><td><b>Phone Number:</b> {r['phone']}</td><td style="text-align: right;"><b>Refd By:</b> {r['doctor']}</td></tr>
            </table>
            <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;">
                <thead><tr style="background-color: #3b82f6; color: white; font-size: 14px;"><th style="padding: 8px; text-align: left;">SL</th><th style="padding: 8px; text-align: left;">Description</th><th style="padding: 8px; text-align: right;">Amount</th></tr></thead>
                <tbody style="font-size: 13px;">
                    {table_rows}
                    <tr style="background-color: #f1f5f9; font-weight: bold;"><td></td><td style="text-align: right; padding: 8px;">Total Amount:</td><td style="text-align: right; padding: 8px;">{r['total']:.2f} ৳</td></tr>
                    <tr><td></td><td style="text-align: right; padding: 6px; color: #475569;">Discount ({r['discount_pct']}%):</td><td style="text-align: right; padding: 6px; color: #475569;">- {r['discount_amt']:.2f} ৳</td></tr>
                    <tr><td></td><td style="text-align: right; padding: 6px; color: #16a34a;">Advance Paid:</td><td style="text-align: right; padding: 6px; color: #16a34a;">{r['advance']:.2f} ৳</td></tr>
                    <tr style="background-color: #fee2e2; color: #b91c1c; font-weight: bold; font-size: 15px; border-top: 2px solid #f87171;"><td></td><td style="text-align: right; padding: 8px;">Due Amount:</td><td style="text-align: right; padding: 8px;">{r['due']:.2f} ৳</td></tr>
                </tbody>
            </table>
            <div style="margin-top: 50px; display: flex; justify-content: flex-end;"><div style="text-align: center; width: 150px;"><hr style="border: none; border-top: 1px solid #475569; margin-bottom: 5px;"><span style="font-size: 12px; font-weight: bold; color: #475569;">Authorized Signature</span></div></div>
        </div>
        """
        st.subheader("🖨️ Receipt Action Menu")
        if st.button("🖨️ Print Receipt Now", type="secondary", use_container_width=True):
            st.components.v1.html("<script>window.print();</script>", height=0, width=0)
        st.components.v1.html(html_receipt, height=580, scrolling=True)

# --- PAGE 2: PATIENT DATABASE ---
elif page == "Patient Database":
    st.title("📋 Patient Record Database")
    st.markdown("---")
    c.execute("SELECT * FROM patients ORDER BY id DESC")
    data = c.fetchall()
    if data:
        columns = ["INV ID", "Patient Name", "Age", "Phone Number", "Referred Doctor", "Selected Tests", "Total Bill", "Discount (%)", "Advance Paid", "Due Amount", "Date"]
        df = pd.DataFrame(data, columns=columns)
        df["INV ID"] = df["INV ID"].apply(lambda x: f"{x:05d}")
        st.dataframe(df, use_container_width=True)
    else: st.info("No records found in the database yet.")

# --- PAGE 3: DOCTORS REPORT DASHBOARD ---
elif page == "Doctors Report":
    st.title("🩺 Doctors Referral & Collection Dashboard")
    st.markdown("---")
    REFERRAL_PERCENTAGE = 10.0 
    c.execute("SELECT * FROM patients ORDER BY id DESC")
    data = c.fetchall()
    if data:
        columns = ["INV ID", "Patient Name", "Age", "Phone Number", "Referred Doctor", "Selected Tests", "Total Bill", "Discount (%)", "Advance Paid", "Due Amount", "Date"]
        df = pd.DataFrame(data, columns=columns)
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        st.subheader("🗓️ Filter by Date Range")
        col_f1, col_f2 = st.columns(2)
        with col_f1: start_date = st.date_input("Start Date", value=df["Date"].min())
        with col_f2: end_date = st.date_input("End Date", value=df["Date"].max())
        filtered_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
        st.markdown("---")
        st.subheader("📊 Doctors Summary")
        if not filtered_df.empty:
            doc_summary = filtered_df.groupby("Referred Doctor")["Total Bill"].sum().reset_index()
            doc_summary.columns = ["Doctor Name", "Total Test Value (TK)"]
            doc_summary[f"Referral Fee ({REFERRAL_PERCENTAGE}%)"] = doc_summary["Total Test Value (TK)"] * (REFERRAL_PERCENTAGE / 100.0)
            total_filtered_bill = filtered_df["Total Bill"].sum()
            total_referral_fee = total_filtered_bill * (REFERRAL_PERCENTAGE / 100.0)
            col_m1, col_m2 = st.columns(2)
            with col_m1: st.metric(label="Total Business Volume (Selected Range)", value=f"{total_filtered_bill:.2f} TK")
            with col_m2: st.metric(label="Total Referral Commission Payable", value=f"{total_referral_fee:.2f} TK")
            st.dataframe(doc_summary, use_container_width=True)
            st.markdown("---")
            st.subheader("📋 Patient Lists under Selected Range")
            display_filtered = filtered_df.copy()
            display_filtered["INV ID"] = display_filtered["INV ID"].apply(lambda x: f"{x:05d}")
            st.dataframe(display_filtered, use_container_width=True)
        else: st.warning("No data found for the selected date range.")
    else: st.info("No data available in database to generate reports.")

