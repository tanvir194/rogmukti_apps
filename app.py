import streamlit as st
import sqlite3
from datetime import datetime

# ডাটাবেজ কানেকশন ও টেবিল তৈরি
def init_db():
    conn = sqlite3.connect("rogmukti.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            phone TEXT,
            doctor TEXT,
            tests TEXT,
            total REAL,
            discount REAL,
            advance REAL,
            due REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_patient(name, age, phone, doctor, tests, total, discount, advance, due, date):
    conn = sqlite3.connect("rogmukti.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO patients (name, age, phone, doctor, tests, total, discount, advance, due, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, age, phone, doctor, tests, total, discount, advance, due, date))
    conn.commit()
    invoice_id = cursor.lastrowid
    conn.close()
    return invoice_id

init_db()
# সাইডবার মেনু তৈরি
page = st.sidebar.selectbox("মেনু সিলেক্ট করুন", ["নতুন পেশেন্ট এন্ট্রি", "আজকের রিপোর্ট"])

# ক্রমিক নম্বরসহ টেস্টের নাম এবং স্ট্যান্ডার্ড দামের তালিকা
TEST_PRICES = {
    # --- Haematology ---
    "01. CBC (Complete Blood Count)": 600.0,
    "02. TC.DC": 250.0,
    "03. HB%": 250.0,
    "04. ESR": 200.0,
    "05. Platelet Count": 300.0,
    "06. MP": 200.0,
    "07. BT/CT": 350.0,
    "08. C/E Count": 250.0,
    # --- Serology ---
    "01. Widal": 450.0,
    "02. Aso Titre": 450.0,
    "03. CRP": 450.0,
    "04. RA/RF": 450.0,
    "05. HBs Ag (Screen Test)": 450.0,
    "06. TPHA": 450.0,
    "07. VDRL": 400.0,
    "08. Group & Rh Factor": 200.0,
    "09. Mantaux-Test (M.T)": 300.0,
    "10. Triple Antigen": 450.0,
    "11. R.Fever": 450.0,
    "12. HIV": 500.0,
    "13. HCV": 500.0,
    "14. TB (ICT)": 750.0,
    "15. Malaria. pf/pv": 700.0,
    "16. H. Pylori": 850.0,
    "17. Fallarlia (ICT)": 750.0,
    "18. Dengue NS1. IGG/IgM": 300.0,
    # --- Hormone Pannel ---
    "01. T3": 1200.0,
    "02. T4": 1200.0,
    "03. FT3": 900.0,
    "04. FT4": 900.0,
    "05. TSH": 1100.0,
    "06. HbA1c": 1500.0,
    "07. Prolactin": 1200.0,
    "08. S. IgE": 1500.0,
    "09. S.IgE (Device Test)": 700.0,
    # --- Bio Chemical Analysis ---
    "01. Random": 200.0,
    "02. Fasting": 200.0,
    "03. 2hr. After Breakfast": 200.0,
    "04. 2hr. After 75gm Glucose": 200.0,
    "05. O.G.T.T": 500.0,
    "06. Blood Urea": 400.0,
    "07. Cholesterol": 350.0,
    "08. HDL": 400.0,
    "09. TG": 350.0,
    "10. LDL": 300.0,
    "11. S.GPT(ALT)": 500.0,
    "12. S.GOT(AST)": 500.0,
    "13. Bilirubin Total": 350.0,
    "14. Lipid Profile": 1000.0,
    "15. Bilirubin Direct/Indirect": 450.0,
    "16. Serum Creatinine": 400.0,
    "17. Uric Acid": 400.0,
    "18. Amylase": 700.0,
    "19. Calcium": 600.0,
    # --- X-Ray Digital ---
    "01. Chest X-Ray": 500.0,
    "02. PNS X-Ray": 500.0,
    "03. Maxila X-Ray": 500.0,
    "04. Nasopharynx X-Ray": 550.0,
    "05. Abdomen A/P X-Ray": 500.0,
    "06. Cervical Spine X-Ray": 600.0,
    "07. Plane X-Ray Abdomen": 500.0,
    "08. Mastoid Towns View X-Ray": 500.0,
    "09. Skull X-Ray": 600.0,
    "10. Pelvic X-Ray": 500.0,
    "11. Mandible B/V X-Ray": 600.0,
    "12. KUB X-Ray": 500.0,
    "13. D/S Spine X-Ray": 600.0,
    "14. L/S Spine X-Ray": 600.0,
    "15. X-ray Foot B/V": 500.0,
    "16. Knee B/V X-Ray": 550.0,
    "17. Elbow B/V X-Ray": 500.0,
    "18. Shoulder Joint B/V X-Ray": 550.0,
    "19. Hip Joint X-Ray": 500.0,
    # --- Urine & Stool Exam ---
    "01. Urine Pregnancy Test (PT)": 200.0,
    "02. Urine R/E": 250.0,
    "03. Stool R/E": 400.0,
    "04. Stool OBT": 400.0,
    # --- UI Ultrasound Imaging ---
    "01. USG Whole Abdomen": 1000.0,
    "02. USG Upper Abdomen": 800.0,
    "03. USG Lower Abdomen": 800.0,
    "04. USG KUB": 1000.0,
    "05. USG Pregnancy Profile": 800.0,
    "06. USG Breast": 1200.0
}if page == "নতুন পেশেন্ট এন্ট্রি":
    st.title("🏥 Rog Mukti Diagnostic Centre")
    st.markdown("---")
    
    if "custom_tests" not in st.session_state:
        st.session_state.custom_tests = {}

    st.subheader("👤 পেসেন্ট এবং ডাক্তারের তথ্য")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name of the PT (পেশেন্টের নাম) *")
        age = st.number_input("Age (বয়স)", min_value=0, max_value=120, value=25)
        phone = st.text_input("Phone (মোবাইল নম্বর)")
    with col2:
        doctor_list = ["ডা. সাইদুল ইসলাম", "ডা. নাসরিন সুলতানা", "ডা. মোতালেব হোসেন", "অন্যান্য"]
        doctor = st.selectbox("REFD By. Dr (ডাক্তার সিলেক্ট করুন)", doctor_list)
        date_input = st.date_input("Date (তারিখ)", datetime.now())
        date_str = date_input.strftime("%Y-%m-%d")

    st.markdown("---")
    st.subheader("🧪 টেস্ট এবং বিলিং সেকশন")

    # স্ট্যান্ডার্ড টেস্ট সার্চ ও সিলেক্ট বক্স
    selected_tests = st.multiselect("Description (এখান থেকে টেস্ট সার্চ বা সিলেক্ট করুন):", options=list(TEST_PRICES.keys()))

    # কাস্টম টেস্ট ইনপুট সেকশন (অটো আপডেট)
    st.markdown("### ➕ তালিকার বাইরের কাস্টম টেস্ট")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        custom_name = st.text_input("কাস্টম টেস্টের নাম লিখুন:", key="c_name_input")
    with c_col2:
        custom_price = st.number_input("টেস্টের রেট (টাকা):", min_value=0.0, step=50.0, key="c_price_input")

    if custom_name:
        st.session_state.custom_tests = {custom_name: float(custom_price)}
    else:
        st.session_state.custom_tests = {}
    # লাইভ বিল ক্যালকুলেশন (স্ট্যান্ডার্ড + কাস্টম টেস্ট)
    sub_total = sum(TEST_PRICES.get(test, 0.0) for test in selected_tests)
    for c_name, c_price in st.session_state.custom_tests.items():
        sub_total += c_price

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"### 🧮 লাইভ টোটাল ফি: `{sub_total}` টাকা")
        discount_pct = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, step=1.0)
        advance = st.number_input("Advance (অগ্রিম পরিশোধ)", min_value=0.0, step=50.0)
        
    with col4:
        discount_amount = sub_total * (discount_pct / 100.0)
        due = sub_total - (discount_amount + advance)
        st.write(f"**ডিসকাউন্ট প্রদেয়:** {discount_amount} টাকা")
        st.metric(label="Due (মোট বাকি টাকা)", value=f"{due} টাকা")

    # ডাটা সেভ করার মূল বাটন লজিক
    if st.button("Save Bill and Generate Receipt (বিল সেভ করুন)"):
        if name and (selected_tests or st.session_state.custom_tests):
            final_tests_list = [t for t in selected_tests]
            for c_name in st.session_state.custom_tests.keys():
                final_tests_list.append(c_name)
            tests_str = ", ".join(final_tests_list)
            
            invoice_id = add_patient(name, age, phone, doctor, tests_str, sub_total, discount_amount, advance, due, date_str)
            
            receipt_tests = []
            for test in selected_tests:
                price = TEST_PRICES.get(test, 0.0)
                receipt_tests.append({"name": test, "price": price})
            for c_name, c_price in st.session_state.custom_tests.items():
                receipt_tests.append({"name": c_name, "price": c_price})

            st.session_state.receipt_data = {
                "inv_no": f"{invoice_id:05d}" if invoice_id else "00001",
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
            st.session_state.custom_tests = {}
            st.success("সফলভাবে ডাটা সেভ হয়েছে!")
            st.rerun()
        elif not name:
            st.error("অনুগ্রহ করে ওপরের ফর্মে পেশেন্টের নাম লিখুন।")
        elif not selected_tests and not st.session_state.custom_tests:
            st.error("অনুগ্রহ করে অন্তত একটি টেস্ট সিলেক্ট বা যোগ করুন।")

elif page == "আজকের রিপোর্ট":
    st.title("📋 আজকের পেশেন্ট রিপোর্ট")
    st.write("আজকের এন্ট্রি করা রোগীদের তালিকা এখানে দেখা যাবে।")
