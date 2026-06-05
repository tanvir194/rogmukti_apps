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
# ৭২ নম্বর লাইন থেকে আপনার ফাইলের একদম শেষ পর্যন্ত পুরো অংশটি মুছে এই কোডটি বসান:

conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()

# ১. নতুন কলাম (referral_fee) সহ টেবিল তৈরি
c.execute('''CREATE TABLE IF NOT EXISTS bills
             (invoice_no TEXT PRIMARY KEY, 
              date TEXT, 
              patient TEXT, 
              age TEXT, 
              phone TEXT,
              doctor TEXT, 
              total REAL, 
              discount REAL, 
              paid REAL, 
              due REAL,
              referral_fee REAL)''')
conn.commit()
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

    # বিল সেভ করার বাটন
    if st.button("Save Bill", key="save_bill_btn"):
        total_real = 1000  
        discount_real = 0
        paid_real = 1000
        due_real = 0
        invoice_no = f"INV-{int(datetime.now().timestamp())}"
        
        # ৩০% রেফারেল ফি অটোমেটিক হিসাব
        ref_fee = total_real * 0.30 
        
        # ডাটাবেজে সেভ করা (১১টি কলাম)
        c.execute("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (invoice_no, date_today.strftime('%Y-%m-%d'), patient_name, age, phone, ref_dr, total_real, discount_real, paid_real, due_real, ref_fee))
        conn.commit()
        st.success("বিল সফলভাবে সেভ হয়েছে!")

with tab2:
    st.header("📊 দৈনিক, साप्ताहिक ও মাসিক ড্যাশবোর্ড")
    
    try:
        # ডাটাবেজ থেকে ডাটা লোড করা
        df = pd.read_sql_query("SELECT * FROM bills", conn)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # ফিল্টার অপশন (অনন্য key ব্যবহার করা হয়েছে)
            filter_option = st.selectbox("হিসাব দেখার সময় নির্বাচন করুন", ["আজ", "এই সপ্তাহ", "এই মাস", "সব সময়"], key="dashboard_time_filter_unique")
            today = datetime.today()
            
            if filter_option == "আজ":
                filtered_df = df[df['date'].dt.date == today.date()]
            elif filter_option == "এই সপ্তাহ":
                start_of_week = today - timedelta(days=today.weekday())
                filtered_df = df[df['date'] >= start_of_week]
            elif filter_option == "এই মাস":
                filtered_df = df[(df['date'].dt.month == today.month) & (df['date'].dt.year == today.year)]
            else:
                filtered_df = df
                
            # সামারি বক্সসমূহ
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("মোট কালেকশন", f"৳ {filtered_df['total'].sum() if 'total' in filtered_df else 0:,.2f}")
            c2.metric("মোট ডিসকাউন্ট", f"৳ {filtered_df['discount'].sum() if 'discount' in filtered_df else 0:,.2f}")
            c3.metric("মোট ডিউ (বাকি)", f"৳ {filtered_df['due'].sum() if 'due' in filtered_df else 0:,.2f}")
            
            ref_sum = filtered_df['referral_fee'].sum() if 'referral_fee' in filtered_df else 0
            c4.metric("মোট রেফারেল ফি (৩০%)", f"৳ {ref_sum:,.2f}")
            
            # রিপোর্ট টেবিল
            st.subheader("👨‍⚕️ ডাক্তার ভিত্তিক রেফারেল রিপোর্ট (নামসহ)")
            if not filtered_df.empty:
                available_cols = [col for col in ['doctor', 'patient', 'invoice_no', 'total', 'referral_fee', 'date'] if col in filtered_df]
                report_display = filtered_df[available_cols]
                st.dataframe(report_display, use_container_width=True)
                
                # প্রিন্ট বাটন
                st.markdown("""
                    <br>
                    <button onclick="window.print()" style="
                        background-color: #4CAF50; 
                        color: white; 
                        padding: 12px 30px; 
                        border: none; 
                        border-radius: 4px; 
                        cursor: pointer;
                        font-size: 16px;
                        font-weight: bold;">
                        🖨️ এই রিপোর্টটি প্রিন্ট করুন
                    </button>
                """, unsafe_allow_html=True)
            else:
                st.warning("নির্বাচিত সময়ে কোনো ডাটা পাওয়া যায়নি।")
        else:
            st.info("ডেটাবেজে এখনো কোনো বিলের রেকর্ড নেই।")
            
    except Exception as e:
        st.info("নতুন ডাটাবেজ তৈরি হচ্ছে। একটি নতুন বিল সেভ করলেই ড্যাশবোর্ড সচল হয়ে যাবে।")

