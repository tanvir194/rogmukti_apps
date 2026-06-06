import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# পেজ কনফিগারেশন
st.set_page_config(page_title="Rog Mukti Diagnostic Centre", layout="wide")

# ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic_final.db", check_same_thread=False)
c = conn.cursor()

# টেবিল তৈরি
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

# ডাটাবেজে তথ্য সেভ করার ফাংশন
def add_patient(name, age, phone, doctor, tests, total, discount, advance, due, date):
    c.execute('''
        INSERT INTO patients (name, age, phone, doctor, tests, total_amount, discount, advance, due, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, phone, doctor, tests, total, discount, advance, due, date))
    conn.commit()
    return c.lastrowid
# টেস্টের নাম এবং স্ট্যান্ডার্ড দামের তালিকা
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
    "Blood Sugar (RBS / Fasting / 22HAB)": 120.0,
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
    
    # --- Urine & Stool ---
    "Urine R/M/E": 200.0,
    "Urine Pregnancy Test (HCG)": 200.0,
    "Stool R/M/E": 200.0,
    "Stool for Occult Blood Test (OBT)": 250.0,
    
    # --- Thyroid & Hormone Panel ---
    "TSH (Thyroid Stimulating Hormone)": 600.0,
    "FT4 (Free Thyroxine)": 600.0,
    "FT3 (Free Triiodothyronine)": 600.0,
    "T3 (Total Triiodothyronine)": 500.0,
    "T4 (Total Thyroxine)": 500.0,
    "Serum Prolactin": 800.0,
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
    
    # --- কাস্টম অপশন (তালিকার বাইরের টেস্টের জন্য) ---
    "Custom Test / অন্যান্য (নিচে নাম ও দাম লিখুন)": 0.0
}
# সাইডবার মেনু নেভিগেশন
st.sidebar.title("🧭 নেভিগেশন মেনু")
page = st.sidebar.radio("অপশন সিলেক্ট করুন:", ["নতুন পেশেন্ট এন্ট্রি", "পেশেন্ট ডাটাবেজ"])

if page == "নতুন পেশেন্ট এন্ট্রি":
    st.title("🏥 Rog Mukti Diagnostic Centre")
    st.markdown("---")
    
    if "receipt_data" not in st.session_state:
        st.session_state.receipt_data = None

    st.subheader("👤 পেশেন্ট এবং ডাক্তারের তথ্য")
    
    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name of the PT (পেশেন্টের নাম) *")
            age = st.number_input("Age (বয়স)", min_value=0, max_value=120, value=25)
            phone = st.text_input("Phone (মোবাইল নম্বর)")
        with col2:
            doctor_list = ["ডা. সাইদুল ইসলাম", "ডা. নাসরিন সুলতানা", "ডা. মোতালেব হোসেন", "Self / অন্যান্য"]
            doctor = st.selectbox("REFd By. Dr (ডাক্তার সিলেক্ট করুন)", doctor_list)
            date_input = st.date_input("Date (তারিখ)", datetime.now())
            date_str = date_input.strftime("%Y-%m-%d")
            
        st.markdown("---")
        st.subheader("🧪 টেস্ট এবং বিলিং সেকশন")
        
        # ড্রপডাউন টেস্ট সিলেকশন
        selected_tests = st.multiselect("Description (এখান থেকে টেস্ট সার্চ বা সিলেক্ট করুন)", sorted(list(TEST_PRICES.keys())))
        
        # কাস্টম টেস্ট লজিক অ্যাক্টিভেশন চেক
        custom_test_active = "Custom Test / অন্যান্য (নিচে নাম ও দাম লিখুন)" in selected_tests
        custom_name = ""
        custom_price = 0.0
        
        if custom_test_active:
            st.info("💡 কাস্টম টেস্ট সিলেক্ট করেছেন। নিচে টেস্টের নাম ও দাম দেওয়ার বক্স সচল হয়েছে।")
            
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if custom_test_active:
                custom_name = st.text_input("কাস্টম টেস্টের নাম লিখুন:")
        with col_c2:
            if custom_test_active:
                custom_price = st.number_input("কাস্টম টেস্টের দাম (টাকা):", min_value=0.0, value=0.0, step=50.0)
        
        # মূল সাবটোটাল এবং কাস্টম টেস্টের দাম যোগ করা
        sub_total = sum(TEST_PRICES[test] for test in selected_tests) + custom_price

        col3, col4 = st.columns(2)
        with col3:
            st.markdown(f"**টোটাল টেস্ট ফি:** {sub_total} টাকা")
            discount_pct = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
            advance = st.number_input("Advance (অগ্রিম পরিশোধ)", min_value=0.0, value=0.0, step=50.0)
        with col4:
            discount_amount = sub_total * (discount_pct / 100)
            due = sub_total - (discount_amount + advance)
            st.write(f"**Discount Amount:** {discount_amount} টাকা")
            st.metric(label="Due (বাকি)", value=f"{due} টাকা")

        submit_btn = st.form_submit_button("Save and Print Bill (ডাটা সেভ করুন)")
        
        if submit_btn:
            if name and selected_tests:
                final_tests_list = [t for t in selected_tests if t != "Custom Test / অন্যান্য (নিচে নাম ও দাম লিখুন)"]
                if custom_test_active and custom_name:
                    final_tests_list.append(f"{custom_name} (Custom)")
                
                tests_str = ", ".join(final_tests_list)
                invoice_id = add_patient(name, age, phone, doctor, tests_str, sub_total, discount_pct, advance, due, date_str)
                
                receipt_tests = []
                for test in selected_tests:
                    if test == "Custom Test / অন্যান্য (নিচে নাম ও দাম লিখুন)":
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
                st.success("তথ্য ডাটাবেজে সেভ হয়েছে! নিচে রঙিন মানি রিসিট তৈরি হয়েছে।")
            elif not name:
                st.error("অনুগ্রহ করে পেশেন্টের নাম লিখুন।")
            elif not selected_tests:
                st.error("অনুগ্রহ করে অন্তত একটি টেস্ট সিলেক্ট করুন।")
    # রিসিট কালার ভিউ রেন্ডারিং
    if st.session_state.receipt_data:
        r = st.session_state.receipt_data
        st.markdown("---")
        st.subheader("📄 প্রাকদর্শন: রঙিন মানি রিসিট")
        
        table_rows = ""
        for i, item in enumerate(r['tests'], 1):
            table_rows += f"""
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 8px; color: #1e293b;">{i}</td>
                <td style="padding: 8px; color: #1e293b;">{item['name']}</td>
                <td style="padding: 8px; text-align: right; color: #1e293b;">{item['price']:.2f} ৳</td>
            </tr>
            """

        html_receipt = f"""
        <div style="border: 3px solid #1e3a8a; padding: 25px; border-radius: 12px; background-color: #f8fafc; font-family: 'Segoe UI', Arial, sans-serif; max-width: 700px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <div style="text-align: center; background-color: #1e3a8a; color: white; padding: 15px; border-radius: 8px 8px 0 0; margin: -25px -25px 20px -25px;">
                <h2 style="margin: 0; font-size: 26px; text-transform: uppercase; letter-spacing: 1px;">Rog Mukti Diagnostic Centre</h2>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Mollah Stand, Auliapur, Patuakhali</p>
                <p style="margin: 2px 0 0 0; font-size: 14px; font-weight: bold;">📞 Phone: 01711867637</p>
            </div>
            
            <div style="text-align: center; margin-bottom: 20px;">
                <span style="background-color: #e2e8f0; padding: 6px 20px; font-weight: bold; border-radius: 20px; color: #0f172a; font-size: 15px; letter-spacing: 1px;">MONEY RECEIPT</span>
            </div>
            
            <table style="width: 100%; font-size: 14px; margin-bottom: 20px; background: white; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <tr>
                    <td style="padding: 4px; color: #1e293b;"><b>Invoice No:</b> <span style="color:#1e3a8a; font-weight:bold;">{r['inv_no']}</span></td>
                    <td style="text-align: right; padding: 4px; color: #1e293b;"><b>Date:</b> {r['date']}</td>
                </tr>
                <tr>
                    <td style="padding: 4px; color: #1e293b;"><b>Patient Name:</b> {r['name']}</td>
                    <td style="text-align: right; padding: 4px; color: #1e293b;"><b>Age:</b> {r['age']} Years</td>
                </tr>
                <tr>
                    <td style="padding: 4px; color: #1e293b;"><b>Phone Number:</b> {r['phone']}</td>
                    <td style="text-align: right; padding: 4px; color: #1e293b;"><b>Refd By:</b> {r['doctor']}</td>
                </tr>
            </table>
            
            <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;">
                <thead>
                    <tr style="background-color: #3b82f6; color: white; font-size: 15px;">
                        <th style="text-align: left; padding: 10px; width: 10%;">SL</th>
                        <th style="text-align: left; padding: 10px; width: 65%;">Description (Test Name)</th>
                        <th style="text-align: right; padding: 10px; width: 25%;">Amount</th>
                    </tr>
                </thead>
                <tbody style="font-size: 14px;">
                    {table_rows}
                    <tr style="background-color: #f1f5f9; font-weight: bold;">
                        <td></td>
                        <td style="text-align: right; padding: 8px; color: #1e293b;">Total Amount:</td>
                        <td style="text-align: right; padding: 8px; color: #1e293b;">{r['total']:.2f} ৳</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td style="text-align: right; padding: 8px; color: #475569;">Discount ({r['discount_pct']}%):</td>
                        <td style="text-align: right; padding: 8px; color: #475569;">- {r['discount_amt']:.2f} ৳</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td style="text-align: right; padding: 8px; color: #16a34a;">Advance Paid:</td>
                        <td style="text-align: right; padding: 8px; color: #16a34a;">{r['advance']:.2f} ৳</td>
                    </tr>
                    <tr style="background-color: #fee2e2; color: #b91c1c; font-weight: bold; font-size: 16px; border-top: 2px solid #f87171;">
                        <td></td>
                        <td style="text-align: right; padding: 10px;">Due (বাকি টাকা):</td>
                        <td style="text-align: right; padding: 10px;">{r['due']:.2f} ৳</td>
                    </tr>
                </tbody>
            </table>
            
            <div style="margin-top: 60px; display: flex; justify-content: flex-end;">
                <div style="text-align: center; width: 150px;">
                    <hr style="border: none; border-top: 1px solid #475569; margin-bottom: 5px;">
                    <span style="font-size: 13px; font-weight: bold; color: #475569;">Authorized Signature</span>
                </div>
            </div>
        </div>
        """
        st.components.v1.html(html_receipt, height=580, scrolling=True)
        st.info("💡 রিসিটটি প্রিন্ট করার জন্য মাউসের রাইট বাটন ক্লিক করে **Print** চাপুন অথবা কিবোর্ড থেকে **Ctrl + P** চাপুন।")

elif page == "পেশেন্ট ডাটাবেজ":
    st.title("📋 রোগমুক্তি ক্লিনিক ডাটাবেজ")
    st.markdown("---")
    
    c.execute("SELECT * FROM patients ORDER BY id DESC")
    data = c.fetchall()
    
    if data:
        columns = ["INV ID", "পেশেন্টের নাম", "বয়স", "মোবাইল নম্বর", "রেফার্ড ডাক্তার", "সিলেক্টেড টেস্ট", "মোট বিল", "ছাড় (%)", "অগ্রিম জমা", "বাকি টাকা", "তারিখ"]
        df = pd.DataFrame(data, columns=columns)
        df["INV ID"] = df["INV ID"].apply(lambda x: f"{x:05d}")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("এখনো ডাটাবেজে কোনো পেশেন্টের তথ্য রেকর্ড করা হয়নি।")

