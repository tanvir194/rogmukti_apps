import streamlit as st
import sqlite3
from datetime import datetime

# পেজ কনফিগারেশন
st.set_page_config(page_title="রোগমুক্তি ডায়াগনস্টিক সেন্টার", page_icon="🏥", layout="wide")

# ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic.db", check_same_thread=False)
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

# ডাক্তারদের তালিকা
doctors_list = ["সিলেক্ট করুন", "ডা. সাইফুল ইসলাম", "ডা. এ. রহমান", "ডা. সুফিয়া খাতুন", "ডা. মোস্তফা কামাল", "ডা. নাসরিন সুলতানা"]

# ১০০+ ডায়াগনস্টিক টেস্ট ও মূল্যের তালিকা
available_tests = {
    # Hematology (রক্ত পরীক্ষা)
    "CBC (Complete Blood Count)": 600,
    "Hgb (Hemoglobin)": 250,
    "ESR (Erythrocyte Sedimentation Rate)": 150,
    "Blood Grouping & Rh Typing": 250,
    "Cross Matching with Screening": 800,
    "BT & CT (Bleeding & Clotting Time)": 200,
    "Platelet Count": 250,
    "WBC Count": 150,
    "Peripheral Blood Smear (PBS)": 500,
    "Malaria Parasite (MP)": 550,
    
    # Biochemistry (বায়োকেমিস্ট্রি)
    "RBS (Random Blood Sugar)": 200,
    "FBS (Fasting Blood Sugar)": 200,
    "2 Hours After Breakfast (2HABF)": 200,
    "HbA1c": 1200,
    "Serum Creatinine": 450,
    "Serum Urea": 450,
    "Serum Uric Acid": 450,
    "Lipid Profile (Full)": 1000,
    "Serum Cholesterol": 350,
    "Triglycerides (TG)": 300,
    "HDL Cholesterol": 300,
    "LDL Cholesterol": 300,
    "Serum Bilirubin (Total)": 500,
    "SGPT (ALT)": 450,
    "SGOT (AST)": 450,
    "Serum Alkaline Phosphatase": 550,
    "Serum Total Protein": 800,
    "Serum Albumin": 650,
    "Serum Calcium": 700,
    "Serum Electrolytes": 1000,
    
    # Serology & Immunology (সেরোলজি)
    "Widal Test (Typhoid)": 450,
    "Febrile Antigen": 800,
    "ASO Titre": 400,
    "RA Factor": 400,
    "CRP (C-Reactive Protein)": 500,
    "HBsAg (Hepatitis B Screening)": 450,
    "HBsAg (Confirmative/ELISA)": 800,
    "Anti-HCV": 600,
    "HIV I & II Screening": 500,
    "VDRL (Syphilis)": 300,
    "TPHA": 400,
    "Dengue NS1 Antigen": 300,
    "Dengue IgG & IgM": 300,
    "Troponin I": 1200,
    
    # Hormone Tests (হরমোন)
    "TSH (Thyroid Stimulating Hormone)": 800,
    "FT4 (Free Thyroxine)": 1000,
    "FT3 (Free Triiodothyronine)": 800,
    "Serum Prolactin": 800,
    "Serum Testosterone": 1000,
    "PSA (Prostate Specific Antigen)": 1200,
    "Beta hCG (Pregnancy)": 1000,
    
    # Urine & Stool (প্রস্রাব ও মল)
    "Urine R/E (Routine Examination)": 250,
    "Urine برای Pregnancy Test (Upt)": 200,
    "Urine Bile Salt & Bile Pigment": 200,
    "Urine Micro-Albumin": 600,
    "Stool R/E": 200,
    "Stool for Occult Blood Test (OBT)": 300,
    
    # Radiology & Imaging (এক্স-রে ও আল্ট্রাসনোগ্রাফি)
    "X-Ray Chest A/P or P/A View": 500,
    "X-Ray Cervical Spine B/V": 800,
    "X-Ray Lumbar Spine B/V": 800,
    "X-Ray KUB (Kidney, Ureter, Bladder)": 600,
    "X-Ray Both Knee Joint B/V": 900,
    "USG of Whole Abdomen": 1200,
    "USG of Upper Abdomen": 800,
    "USG of Lower Abdomen": 800,
    "USG of KUB Region": 800,
    "USG of Pregnancy/Pelvis": 700,
    "USG of Breast (Unilateral)": 1000,
    "USG of Thyroid Gland": 1000,
    
    # Cardiology & Neurology
    "ECG (Electrocardiogram)": 400,
    "Echocardiography (2D & Doppler)": 2000,
    "ETT (Exercise Tolerance Test)": 3000,
    "EEG": 2500,
    
    # Tumor Markers & Others
    "AFP (Alpha Fetoprotein)": 1000,
    "CEA (Carcinoembryonic Antigen)": 1200,
    "CA-125 (Ovarian Cancer)": 1500,
    "Semen Analysis": 500,
    "Skin Scraping for Fungus": 300,
    "ASO Titre (Quantitative)": 600,
    "Fluid RE (Ascitic/Pleural)": 800
}

# সাইডবার মেনু
st.sidebar.header("🏥 নেভিগেশন মেনু")
menu = st.sidebar.radio("অপশন সিলেক্ট করুন:", ["নতুন পেশেন্ট এন্ট্রি", "বিলিং ও রিসিট", "পেশেন্ট ডাটাবেজ"])

st.title("🏥 রোগমুক্তি ক্লিনিক ম্যানেজমেন্ট সিস্টেম")
st.write("---")
# ১. নতুন পেশেন্ট এন্ট্রি
if menu == "নতুন পেশেন্ট এন্ট্রি":
    st.subheader("👤 পেশেন্ট এবং ডাক্তারের তথ্য")
    
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Name of the PT (পেশেন্টের নাম)")
        age = st.number_input("Age (বয়স)", min_value=1, max_value=120, value=25)
        phone = st.text_input("Phone (মোবাইল নম্বর)")
    
    with col2:
        doctor = st.selectbox("REFD BY. DR (ডাক্তার সিলেক্ট করুন)", doctors_list)
        date_today = st.date_input("Date (তারিখ)", datetime.now())

    st.write("---")
    st.subheader("🧪 টেস্ট এবং বিলিং")
    
    # ড্রপডাউন তালিকা (১০০+ টেস্ট সিলেক্ট করার জন্য)
    selected_tests = st.multiselect("Description (এখান থেকে সার্চ বা সিলেক্ট করুন)", list(available_tests.keys()))
    
    # প্রাথমিক মোট বিল হিসাব
    subtotal = sum(available_tests[test] for test in selected_tests)
    st.markdown(f"#### 💰 সাব-টোটাল: **{subtotal} টাকা**")
    
    col3, col4 = st.columns(2)
    with col3:
        discount_pct = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=0.0)
        advance = st.number_input("Advance (অগ্রিম পরিশোধ)", min_value=0.0, value=0.0)
    
    # ডিসকাউন্ট এবং ডিউ হিসাব
    discount_amount = (subtotal * discount_pct) / 100
    total_amount = subtotal - discount_amount
    due = total_amount - advance
    
    with col4:
        st.write("")
        st.markdown(f"**Total Amount:** {total_amount} টাকা")
        st.markdown(f"**Due (বাকি):** <span style='color:red;font-weight:bold;'>{due} টাকা</span>", unsafe_allow_html=True)
    
    st.write("")
    if st.button("Save and Print Baton (ডাটা সেভ করুন)"):
        if patient_name and phone and doctor != "সিলেক্ট করুন" and selected_tests:
            tests_str = "||".join(selected_tests) # টেস্টগুলো আলাদা করার জন্য
            c.execute("""
                INSERT INTO patients (name, age, phone, doctor, tests, total_amount, discount, advance, due, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (patient_name, age, phone, doctor, tests_str, total_amount, discount_pct, advance, due, str(date_today)))
            conn.commit()
            st.success(f"✅ {patient_name}-এর তথ্য সফলভাবে ডাটাবেজে সেভ হয়েছে! ইনভয়েস প্রিন্ট করতে 'বিলিং ও রিসিট' মেনুতে যান।")
        else:
            st.error("⚠️ দয়া করে সব তথ্য সঠিকভাবে পূরণ করুন এবং অন্তত একটি টেস্ট সিলেক্ট করুন।")
            # ২. বিলিং ও রিসিট
elif menu == "বিলিং ও রিসিট":
    st.subheader("🧾 পেশেন্ট রিসিট ও ইনভয়েস প্রিন্ট")
    phone_search = st.text_input("পেশেন্টের মোবাইল নম্বর দিয়ে খুঁজুন")
    
    if phone_search:
        c.execute("SELECT * FROM patients WHERE phone = ? ORDER BY id DESC", (phone_search,))
        p = c.fetchone()
        
        if p:
            # প্রিন্ট লেআউট
            st.markdown(
                f"""
                <div style="border: 2px solid #000; padding: 20px; font-family: 'Courier New', Courier, monospace; width: 100%; max-width: 600px; margin: auto; background-color: #fff; color: #000;">
                    <!-- হেডার সেকশন -->
                    <div style="text-align: center; margin-bottom: 10px;">
                        <h2 style="margin: 0; font-size: 24px; font-weight: bold;">Rog Mukti Diagnostic Centre</h2>
                        <p style="margin: 3px 0; font-size: 14px;">Mollah stand, Auliapur</p>
                        <p style="margin: 3px 0; font-size: 14px;">Patuakhali</p>
                        <p style="margin: 3px 0; font-size: 14px; font-weight: bold;">Phone: 01711867637</p>
                        <h3 style="margin: 15px 0 10px 0; text-decoration: underline; font-size: 18px; letter-spacing: 2px;">MONEY RECEIPT</h3>
                    </div>
                    
                    <!-- পেশেন্ট ইনফো -->
                    <table style="width: 100%; margin-bottom: 15px; font-size: 14px; border: none;">
                        <tr>
                            <td style="width: 50%;"><strong>INV No:</strong> #0000{p[0]}</td>
                            <td style="text-align: right;"><strong>Date:</strong> {p[10]}</td>
                        </tr>
                        <tr>
                            <td colspan="2" style="padding-top: 5px;"><strong>Name of the PT:</strong> {p[1]}</td>
                        </tr>
                        <tr>
                            <td colspan="2" style="padding-top: 5px;"><strong>Age:</strong> {p[2]} Years</td>
                        </tr>
                        <tr>
                            <td colspan="2" style="padding-top: 5px;"><strong>Refd By. Dr:</strong> {p[4]}</td>
                        </tr>
                    </table>
                    
                    <!-- টেস্ট টেবিল সেকশন -->
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 14px;">
                        <thead>
                            <tr style="border-top: 1px solid #000; border-bottom: 1px solid #000;">
                                <th style="border: 1px solid #000; padding: 5px; text-align: center; width: 10%;">SL</th>
                                <th style="border: 1px solid #000; padding: 5px; text-align: left; width: 65%;">Description</th>
                                <th style="border: 1px solid #000; padding: 5px; text-align: right; width: 25%;">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                """, unsafe_allow_html=True
            )
            
            # টেস্টের তালিকা লুপ করে টেবিলে বসানো
            tests_array = p[5].split("||")
            for idx, t_name in enumerate(tests_array, start=1):
                t_cost = available_tests.get(t_name, 0)
                st.markdown(
                    f"""
                            <tr>
                                <td style="border: 1px solid #000; padding: 5px; text-align: center;">{idx}</td>
                                <td style="border: 1px solid #000; padding: 5px;">{t_name}</td>
                                <td style="border: 1px solid #000; padding: 5px; text-align: right;">{t_cost:.2f}</td>
                            </tr>
                    """, unsafe_allow_html=True
                )
            
            # টেবিলের নিচের টোটাল হিসাব অংশ
            subtotal_calc = sum(available_tests.get(t, 0) for t in tests_array)
            st.markdown(
                f"""
                            <tr style="border-top: 2px solid #000;">
                                <td colspan="2" style="border: 1px solid #000; padding: 5px; text-align: right; font-weight: bold;">Total Amount =</td>
                                <td style="border: 1px solid #000; padding: 5px; text-align: right; font-weight: bold;">{subtotal_calc:.2f}</td>
                            </tr>
                            <tr>
                                <td colspan="2" style="border: 1px solid #000; padding: 5px; text-align: right;">Discount =</td>
                                <td style="border: 1px solid #000; padding: 5px; text-align: right;">{p[7]}%</td>
                            </tr>
                            <tr>
                                <td colspan="2" style="border: 1px solid #000; padding: 5px; text-align: right;">Advance =</td>
                                <td style="border: 1px solid #000; padding: 5px; text-align: right;">{p[8]:.2f}</td>
                            </tr>
                            <tr style="font-weight: bold; background-color: #f2f2f2;">
                                <td colspan="2" style="border: 1px solid #000; padding: 5px; text-align: right;">Due =</td>
                                <td style="border: 1px solid #000; padding: 5px; text-align: right;">{p[9]:.2f}</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <!-- সিগনেচার এরিয়া -->
                    <div style="margin-top: 50px; text-align: right; font-size: 14px;">
                        <span style="border-top: 1px dashed #000; padding-top: 5px;">Signature</span>
                    </div>
                </div>
                <br>
                """, unsafe_allow_html=True
            )
            
            st.button("প্রিন্ট করুন (Ctrl + P)")
        else:
            st.warning("🔍 এই মোবাইল নম্বরে কোনো পেশেন্ট ডাটা পাওয়া যায়নি।")

# ৩. পেশেন্ট ডাটাবেজ
elif menu == "পেশেন্ট ডাটাবেজ":
    st.subheader("📊 নিবন্ধিত পেশেন্টদের তালিকা")
    c.execute("SELECT id, name, age, phone, doctor, total_amount, due, date FROM patients ORDER BY id DESC")
    data = c.fetchall()
    
    if data:
        st.table([
            {"INV No": f"#0000{row[0]}", "Name": row[1], "Age": row[2], "Phone": row[3], "Doctor": row[4], "Total (Tk)": row[6], "Due (Tk)": row[9], "Date": row[10]}
            for row in data
        ])
    else:
        st.info("এখনো কোনো পেশেন্টের তথ্য ডাটাবেজে রেকর্ড করা হয়নি।")

conn.close()
