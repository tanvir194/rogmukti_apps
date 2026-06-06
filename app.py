import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# 1. Page Configuration Settings
st.set_page_config(
    page_title="Rog Mukti Diagnostic Centre", 
    layout="wide"
)

# 2. Database Connection Setup
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

# 3. Master Price List Dictionary
TEST_PRICES = {

# --- Haematology & Blood ---
    "CBC (Complete Blood Count)": 400.0,
    "Hgb (Hemoglobin)": 150.0,
    "ESR (Erythrocyte Sedimentation Rate)": 150.0,
    "WBC Count & DC": 250.0,
    "Platelet Count": 200.0,
    "Blood Grouping & Rh Typing": 150.0,
    "BT & CT (Bleeding & Clotting Time)": 200.0,
    "PBF (Peripheral Blood Film)": 450.0,
    "Malaria Parasite (MP)": 200.0,
    
    # --- Biochemistry & Diabetes ---
    "Blood Sugar (RBS / Fasting / 2H HAB)": 120.0,
    "HbA1c": 800.0,
    "Serum Creatinine": 300.0,
    "Serum Bilirubin (Total/Direct)": 250.0,
    "SGPT (ALT)": 350.0,
    "SGOT (AST)": 350.0,
    "Serum Alkaline Phosphatase": 350.0,
    "Lipid Profile (Full)": 1000.0,
    "Serum Cholesterol": 250.0,
    "Serum Triglycerides": 350.0,
    "Serum Uric Acid": 350.0,
    "Serum Urea / BUN": 300.0,
    "Serum Electrolytes (Na, K, Cl)": 1000.0,
    "Serum Calcium": 400.0,
    
    # --- Serology & Immunology ---
    "HBsAg (Screening / ELISA)": 350.0,
    "Anti-HCV": 600.0,
    "HIV I & II": 500.0,
    "Widal Test (Typhoid)": 350.0,
    "ASO Titre": 400.0,
    "RA Factor": 400.0,
    "CRP (C-Reactive Protein)": 500.0,
    "Dengue NS1 Antigen": 600.0,
    "Dengue IgG/IgM": 700.0,
    "Chikungunya IgM": 800.0,
    "Troponin I (Cardiac)": 1200.0,
    
    # --- Urine, Hormone & Imaging ---
    "Urine R/M/E": 200.0,
    "TSH (Thyroid Stimulating Hormone)": 600.0,
    "FT4 (Free Thyroxine)": 600.0,
    "ECG (Electrocardiogram)": 400.0,
    "ETT (Exercise Tolerance Test)": 3000.0,
    "USG of Whole Abdomen": 1500.0,
    "USG of Pregnancy / Obstetric": 800.0,
    "X-Ray Chest P/A View (Digital)": 500.0,
    
    # --- Custom Test Option ---
    "Custom Test / Others (Type Name & Price Below)": 0.0
}
# 4. Sidebar Navigation Menu Options
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
    selected_tests = st.multiselect("Description (Search or select tests)", sorted(list(TEST_PRICES.keys())))
    
    custom_test_active = "Custom Test / Others (Type Name & Price Below)" in selected_tests
    custom_name, custom_price = "", 0.0
    
    if custom_test_active:
        st.info("💡 Custom Test is active. Please enter name and price below.")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if custom_test_active: 
            custom_name = st.text_input("Enter Custom Test Name:")
    with col_c2:
        if custom_test_active: 
            custom_price = st.number_input("Enter Custom Test Price (TK):", min_value=0.0, value=0.0, step=50.0)
    
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
    if st.button("💾 Save Bill and Generate Receipt", type="primary", use_container_width=True):
        if name and selected_tests:
            final_tests_list = [t for t in selected_tests if t != "Custom Test / Others (Type Name & Price Below)"]
            if custom_test_active and custom_name: 
                final_tests_list.append(f"{custom_name} (Custom)")
            tests_str = ", ".join(final_tests_list)
            invoice_id = add_patient(name, age, phone, doctor, tests_str, sub_total, discount_pct, advance, due, date_str)
            receipt_tests = [{"name": t, "price": TEST_PRICES[t]} for t in selected_tests if t != "Custom Test / Others (Type Name & Price Below)"]
            if custom_test_active and custom_name: 
                receipt_tests.append({"name": custom_name, "price": custom_price})
            st.session_state.receipt_data = {"inv_no": f"{invoice_id:05d}", "date": date_str, "name": name, "age": age, "doctor": doctor, "phone": phone, "tests": receipt_tests, "total": sub_total, "discount_pct": discount_pct, "discount_amt": discount_amount, "advance": advance, "due": due}
            st.success("Data saved successfully! Print menu and invoice are available below.")
        elif not name: 
            st.error("Please enter the Patient's Name.")
        elif not selected_tests: 
            st.error("Please select at least one test.")
if st.session_state.receipt_data:
        r = st.session_state.receipt_data
        table_rows = "".join([f"<tr><td>{i}</td><td>{item['name']}</td><td style='text-align:right;'>{item['price']:.2f} ৳</td></tr>" for i, item in enumerate(r['tests'], 1)])
        html_receipt = f"""<div style='border: 3px solid #1e3a8a; padding: 25px; border-radius: 12px; background-color: #f8fafc; font-family: sans-serif; max-width: 650px; margin: 0 auto;'><div style='text-align: center; background-color: #1e3a8a; color: white; padding: 15px; border-radius: 8px 8px 0 0; margin: -25px -25px 20px -25px;'><h2 style='margin: 0;'>Rog Mukti Diagnostic Centre</h2><p style='margin: 5px 0 0 0; font-size: 13px;'>Mollah Stand, Patuakhali</p></div><div style='text-align: center; margin-bottom: 15px;'><span style='background-color: #e2e8f0; padding: 5px 18px; font-weight: bold; border-radius: 20px; color: #0f172a; font-size: 14px;'>MONEY RECEIPT</span></div><table style='width: 100%; font-size: 13px; margin-bottom: 15px;'><tr><td><b>Inv No:</b> {r['inv_no']}</td><td style='text-align: right;'><b>Date:</b> {r['date']}</td></tr><tr><td><b>Name:</b> {r['name']}</td><td style='text-align: right;'><b>Age:</b> {r['age']} Yrs</td></tr><tr><td><b>Phone:</b> {r['phone']}</td><td style='text-align: right;'><b>Refd By:</b> {r['doctor']}</td></tr></table><table style='width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;'><thead><tr style='background-color: #3b82f6; color: white;'><th style='padding: 8px; text-align: left;'>SL</th><th style='padding: 8px; text-align: left;'>Description</th><th style='padding: 8px; text-align: right;'>Amount</th></tr></thead><tbody>{table_rows}<tr style='background-color: #f1f5f9; font-weight: bold;'><td></td><td style='text-align: right; padding: 8px;'>Total:</td><td style='text-align: right; padding: 8px;'>{r['total']:.2f} ৳</td></tr><tr><td></td><td style='text-align: right; padding: 6px;'>Discount ({r['discount_pct']}%):</td><td style='text-align: right; padding: 6px;'>- {r['discount_amt']:.2f} ৳</td></tr><tr><td></td><td style='text-align: right; padding: 6px;'>Advance:</td><td style='text-align: right; padding: 6px;'>{r['advance']:.2f} ৳</td></tr><tr style='background-color: #fee2e2; color: #b91c1c; font-weight: bold;'><td></td><td style='text-align: right; padding: 8px;'>Due:</td><td style='text-align: right; padding: 8px;'>{r['due']:.2f} ৳</td></tr></tbody></table></div>"""
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
