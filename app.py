import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")

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

# SQLite ডাটাবেস আপডেট (Due কলাম সহ)
conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bills
             (invoice_no TEXT PRIMARY KEY, date TEXT, patient TEXT, age TEXT, phone TEXT, 
              doctor TEXT, total REAL, discount REAL, paid REAL, due REAL)''')
conn.commit()

# ডাটাবেসে due কলাম চেক ও এড করা
try:
    c.execute("ALTER TABLE bills ADD COLUMN due REAL DEFAULT 0")
    conn.commit()
except:
    pass

tab1, tab2 = st.tabs(["📑 Billing / Cash Memo", "📊 Dashboard"])

with tab1:
    st.subheader("👤 Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name:")
        age = st.text_input("Age:")
        phone = st.text_input("Phone Number:")
    with col2:
        ref_dr = st.selectbox("Referred By:", doctors_list)
        date_today = st.date_input("Date:", datetime.now())

    st.divider()
    st.subheader("🧪 Test Selection (Unlimited)")
    
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
    st.subheader("💰 Payment Details")
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
            
            c.execute("SELECT COUNT(*) FROM bills")
            count = c.fetchone()[0]
            invoice_no = f"ROG-{today_str}-{count+1:03d}"
            
            c.execute("""INSERT OR REPLACE INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (invoice_no, str(date_today), patient_name, age, phone, ref_dr, total_amount, discount, paid_amount, due_amount))
            conn.commit()
            
            st.success(f"✅ Invoice Saved! Invoice No: **{invoice_no}**")
            
            memo_html = f"""
            <div style="font-family: Arial; max-width: 600px; margin: auto; padding: 30px; border: 3px solid black; background: white; color: black;">
                <h2 style="text-align: center; color: red; margin-bottom:5px;">ROGMUKTI DIAGNOSTIC CENTRE</h2>
                <p style="text-align: center; margin-top:0;">Mollah Bazar, Auliapur, Patuakhali | 01711-867637</p>
                <p style="text-align: center; font-size: 12px; font-weight: bold;">Invoice No: {invoice_no}</p>
                <hr>
                <table style="width:100%; font-size:14px;">
                    <tr><td><b>Patient:</b> {patient_name}</td><td style="text-align:right;"><b>Date:</b> {date_today}</td></tr>
                    <tr><td><b>Age/Sex:</b> {age}</td><td style="text-align:right;"><b>Doctor:</b> {ref_dr}</td></tr>
                    <tr><td><b>Phone:</b> {phone}</td><td></td></tr>
                </table>
                <hr>
                <table style="width:100%; border-collapse:collapse; font-size:14px;">
                    <tr style="background:#f0f0f0; font-weight:bold;">
                        <td style="padding:8px; border:1px solid #ddd; width:40px;">Sl.</td>
                        <td style="padding:8px; border:1px solid #ddd;">Test Name</td>
                        <td style="padding:8px; border:1px solid #ddd; text-align:right;">Price</td>
                    </tr>
                    {test_list_html}
                </table>
                <hr>
                <table style="width:100%; font-weight:bold; font-size:15px;">
                    <tr><td style="text-align:right;">Total Amount:</td><td style="text-align:right; width:120px;">{total_amount} TK</td></tr>
                    <tr><td style="text-align:right; color:red;">Discount:</td><td style="text-align:right; color:red;">{discount} TK</td></tr>
                    <tr><td style="text-align:right; color:blue;">Total Paid:</td><td style="text-align:right; color:blue;">{paid_amount} TK</td></tr>
                    <tr style="font-size:17px; color:{'red' if due_amount > 0 else 'green'};">
                        <td style="text-align:right;">Due (বাকি):</td>
                        <td style="text-align:right;">{due_amount} TK</td>
                    </tr>
                </table>
                <p style="text-align:center; margin-top:25px; font-weight:bold;">Thank You!</p>
            </div>
            """
            st.components.v1.html(memo_html, height=550)
            st.markdown('<button onclick="window.print()" style="background:#28a745;color:white;padding:12px 25px;font-size:17px;border:none;border-radius:5px;width:100%;margin-top:10px;font-weight:bold;cursor:pointer;">🖨️ Print Cash Memo</button>', unsafe_allow_html=True)
        else:
            st.error("Patient Name, Doctor এবং কমপক্ষে ১টি Test সিলেক্ট করুন।")

with tab2:
    st.header("📊 Advanced Analytics Dashboard")
    df_db = pd.read_sql_query("SELECT * FROM bills", conn)
    
    if not df_db.empty:
        df = df_db.rename(columns={
            'invoice_no': 'Invoice_No', 'patient': 'Patient', 'age': 'Age',
            'phone': 'Phone', 'doctor': 'Doctor', 'total': 'Total',
            'discount': 'Discount', 'paid': 'Paid', 'due': 'Due'
        })
        df['Date'] = pd.to_datetime(df_db['date']).dt.date
    else:
        df = pd.DataFrame(columns=["Invoice_No", "Date", "Patient", "Age", "Phone", "Doctor", "Total", "Discount", "Paid", "Due"])

    if not df.empty:
        today = datetime.now().date()
        
        st.subheader("🔍 Filter Records")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("From Date", value=today.replace(day=1), key="dash_start")
        with col_d2:
            end_date = st.date_input("To Date", value=today, key="dash_end")
        
        filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        
        # চার কাউন্টার ম্যাট্রিক্স
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Collected", f"৳ {filtered_df['Paid'].sum():,.0f}")
        m2.metric("Total Discount", f"৳ {filtered_df['Discount'].sum():,.0f}")
        m3.metric("Total Due (বাকি)", f"৳ {filtered_df['Due'].sum():,.0f}", delta_color="inverse")
        m4.metric("Total Patients", f"{len(filtered_df)} জন")
        
        # --- বিল্ট-ইন বার চার্ট সেকশন ---
        st.divider()
        st.subheader("📈 Daily Collection Trend")
        if not filtered_df.empty:
            daily_sales = filtered_df.groupby('Date')['Paid'].sum()
            st.bar_chart(daily_sales, color="#1f77b4")
            
            st.subheader("👨‍⚕️ Doctor Wise Business Summary")
            doc_sales = filtered_df.groupby('Doctor')['Total'].sum()
            st.bar_chart(doc_sales, color="#ff7f0e")

        # --- ডাক্তারদের রেফারেল স্টেটমেন্ট ও মাসিক প্রিন্ট ---
        st.divider()
        st.subheader("👨‍⚕️ Doctor Statement & Print Report")
        selected_doc = st.selectbox("Select Doctor for Monthly Report", doctors_list[1:], key="report_doc_select")
        
        if selected_doc:
            doc_df = filtered_df[filtered_df['Doctor'] == selected_doc]
            if not doc_df.empty:
                doc_total = doc_df['Total'].sum()
                referral_fee = doc_total * 0.30
                
                st.info(f"📊 **{selected_doc}** এর মোট বিজনেস: ৳ {doc_total:,.0f} | রেফারেল ফি (৩০%): **৳ {referral_fee:,.0f}**")

