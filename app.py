import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")

# ইনপুট বক্স, ড্রপডাউন এবং সিলেকশন বক্সের ভেতরের ঘরগুলো রঙিন করার CSS
st.markdown("""
<style>
    /* ১. রোগী ও ডাক্তারের পুরো সেকশনের ব্যাকগ্রাউন্ড */
    .section-box-blue { background-color: #f1f8ff; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    /* ২. টেস্ট লিস্ট সেকশনের ব্যাকগ্রাউন্ড */
    .section-box-green { background-color: #f4faf6; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    /* ৩. পেমেন্ট সেকশনের ব্যাকগ্রাউন্ড */
    .section-box-orange { background-color: #fff9f0; padding: 12px; border-radius: 5px; margin-bottom: 10px; }

    /* লেখার ও সিলেক্ট করার মূল ইনপুট ঘরগুলোর ভেতরের কালার স্টাইল */
    .stTextInput input {
        background-color: #e3f2fd !important;
        border: 1px solid #1e88e5 !important;
        color: black !important;
        font-weight: bold !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #e0f7fa !important;
        border: 1px solid #00bcd4 !important;
        font-weight: bold !important;
    }
    .stMultiSelect div[data-baseweb="select"] {
        background-color: #e8f5e9 !important;
        border: 1px solid #43a047 !important;
        font-weight: bold !important;
    }
    .stNumberInput input {
        background-color: #fffde7 !important;
        border: 1px solid #fbc02d !important;
        color: black !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Market, Galachipa, Patuakhali</p>", unsafe_allow_html=True)

# ডাক্তারদের তালিকা
doctors_list = ["Select Doctor", "Self / Direct", "Dr. Saiful Islam", "Dr. A. Rahman", "Dr. S. Islam"]

# টেস্টের তালিকা এবং আসল দাম (এখানে আপনার ডায়াগনস্টিকের টেস্ট ও দামগুলো বসিয়ে নিন)
test_directory = {
    "Select Test": 0,
    "CBC (Complete Blood Count)": 400,
    "Lipid Profile": 1000,
    "RBS (Random Blood Sugar)": 150,
    "Serum Creatinine": 350,
    "Urine RE": 250,
    "Ultrasonography (USG)": 1200,
    "X-Ray Chest Chest PA View": 500,
    "ECG": 400,
    "HBsAg": 350,
    "Blood Grouping & Rh Typing": 150
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
    
    # মাল্টিপল টেস্ট সিলেক্ট করার ড্রপডাউন (Select Test বাদ দিয়ে)
    available_tests = [test for test in test_directory.keys() if test != "Select Test"]
    selected_tests = st.multiselect("Select Tests:", available_tests)
    
    # সিলেক্ট করা টেস্টের দাম হিসাব ও টেবিল তৈরি
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
        # মোট বিল থেকে ডিসকাউন্ট বাদ দিয়ে আসল বিল
        net_total = max(0.0, total_amount - discount)
        paid = st.number_input("Paid Amount (জমা ৳):", min_value=0.0, max_value=net_total, step=50.0, value=net_total)
    with col6:
        due = max(0.0, net_total - paid)
        st.metric(label="Due Amount (বাকি বিল):", value=f"৳ {due:,.2f}")

    # বিল সেভ এবং রসিদ প্রিন্ট করার বাটন
    if st.button("Save Bill & Generate Invoice", key="save_bill_btn", type="primary"):
        if not patient_name:
            st.error("অনুগ্রহ করে রোগীর নাম লিখুন!")
        elif not selected_tests:
            st.error("অনুগ্রহ করে অন্তত একটি টেস্ট সিলেক্ট করুন!")
        else:
            invoice_no = f"INV-{int(datetime.now().timestamp())}"
            
            # ডাক্তারের ৩০% রেফারেল ফি স্বয়ংক্রিয় হিসাব (মোট বিলের ওপর)
            ref_fee = total_amount * 0.30 
            
            # ডাটাবেজে রোগীর সম্পূর্ণ তথ্য সংরক্ষণ
            c.execute("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (invoice_no, date_today.strftime('%Y-%m-%d'), patient_name, age, phone, ref_dr, total_amount, discount, paid, due, ref_fee))
            conn.commit()
            st.success(f"বিল সফলভাবে সেভ হয়েছে! ইনভয়েস নম্বর: {invoice_no}")
            
            # রোগীকে রসিদ বা ক্যাশ মেমো দেওয়ার জন্য প্রিন্ট উইন্ডো চালু করা
            st.markdown("### 📄 রোগীর ক্যাশ মেমো (রসিদ)")
            st.write(f"**Invoice No:** {invoice_no} | **Date:** {date_today.strftime('%d-%m-%Y')}")
            st.write(f"**Patient Name:** {patient_name} | **Age:** {age} | **Phone:** {phone}")
            st.write(f"**Referred By:** {ref_dr}")
            st.dataframe(pd.DataFrame(test_rows), use_container_width=True)
            st.write(f"**Total:** ৳{total_amount} | **Discount:** ৳{discount} | **Paid:** ৳{paid} | **Due:** ৳{due}")
            
            st.markdown("""
                <script>window.print();</script>
            """, unsafe_allow_html=True)

with tab2:
    st.header("📊 দৈনিক, साप्ताहिक ও মাসিক ড্যাশবোর্ড")
    
    try:
        df = pd.read_sql_query("SELECT * FROM bills", conn)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # ফিল্টার অপশন
            filter_option = st.selectbox("হিসাব দেখার সময় নির্বাচন করুন", ["আজ", "এই সপ্তাহ", "এই মাস", "সব সময়"], key="dashboard_time_filter_final")
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
                
            # সামারি বক্সসমূহ (কাউন্টার বক্স)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("মোট কালেকশন", f"৳ {filtered_df['total'].sum() if 'total' in filtered_df else 0:,.2f}")
            c2.metric("মোট ডিসকাউন্ট", f"৳ {filtered_df['discount'].sum() if 'discount' in filtered_df else 0:,.2f}")
            c3.metric("মোট ডিউ (বাকি)", f"৳ {filtered_df['due'].sum() if 'due' in filtered_df else 0:,.2f}")
            
            ref_sum = filtered_df['referral_fee'].sum() if 'referral_fee' in filtered_df else 0
            c4.metric("মোট রেফারেল ফি (৩০%)", f"৳ {ref_sum:,.2f}")
            
            # ডাক্তার ভিত্তিক রিপোর্ট টেবিল
            st.subheader("👨‍⚕️ ডাক্তার ভিত্তিক রেফারেল রিপোর্ট (নামসহ)")
            if not filtered_df.empty:
                available_cols = [col for col in ['doctor', 'patient', 'invoice_no', 'total', 'referral_fee', 'date'] if col in filtered_df]
                report_display = filtered_df[available_cols]
                st.dataframe(report_display, use_container_width=True)
                
                # ড্যাশবোর্ড রিপোর্ট প্রিন্ট বাটন
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
                        🖨️ এই ড্যাশবোর্ড রিপোর্টটি প্রিন্ট করুন
                    </button>
                """, unsafe_allow_html=True)
            else:
                st.warning("নির্বাচিত সময়ে কোনো ডাটা পাওয়া যায়নি।")
        else:
            st.info("ডেটাবেজে এখনো কোনো বিলের রেকর্ড নেই।")
            
    except Exception as e:
        st.info("নতুন ডাটাবেজ তৈরি হচ্ছে। একটি নতুন বিল সেভ করলেই ড্যাশবোর্ড সচল হয়ে যাবে।")


