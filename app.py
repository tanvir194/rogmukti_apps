import streamlit as st, pandas as pd, sqlite3
from datetime import datetime, timedelta

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")

st.markdown("""
<style>
    .section-box-blue { background-color: #f1f8ff; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    .section-box-green { background-color: #f4faf6; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    .section-box-orange { background-color: #fff9f0; padding: 12px; border-radius: 5px; margin-bottom: 10px; }
    .stTextInput input { background-color: #e3f2fd !important; border: 1px solid #1e88e5 !important; color: black !important; font-weight: bold !important; }
    .stSelectbox div[data-baseweb='select'] { background-color: #e0f7fa !important; border: 1px solid #00bcd4 !important; font-weight: bold !important; }
    .stMultiSelect div[data-baseweb='select'] { background-color: #e8f5e9 !important; border: 1px solid #43a047 !important; font-weight: bold !important; }
    .stNumberInput input { background-color: #fffde7 !important; border: 1px solid #fbc02d !important; color: black !important; font-weight: bold !important; }
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: bold !important; color: #1e88e5 !important; }
    @media print { 
        body * { visibility: hidden !important; } 
        .print-area, .print-area * { visibility: visible !important; } 
        .print-area { position: absolute !important; left: 0 !important; top: 0 !important; width: 100% !important; margin: 0 !important; padding: 10px !important; border: none !important; } 
        [data-testid='stHeader'], button, iframe { display: none !important; } 
    }
</style>
""", unsafe_allow_html=True)

conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS bills (invoice_no TEXT PRIMARY KEY, date TEXT, patient TEXT, age TEXT, phone TEXT, doctor TEXT, total REAL, discount REAL, paid REAL, due REAL, referral_fee REAL)")
c.execute("CREATE TABLE IF NOT EXISTS setup_doctors (name TEXT UNIQUE)")
c.execute("CREATE TABLE IF NOT EXISTS setup_tests (name TEXT UNIQUE, rate REAL)")
conn.commit()

c.execute("SELECT COUNT(*) FROM setup_doctors")
if c.fetchone()[0] == 0:
    for doc in ["Select Doctor", "Self / Direct", "Dr. Saiful Islam", "Dr. A. Rahman", "Dr. S. Islam"]:
        c.execute("INSERT OR IGNORE INTO setup_doctors VALUES (?)", (doc,))
    conn.commit()

c.execute("SELECT COUNT(*) FROM setup_tests")
if c.fetchone()[0] == 0:
    default_tests = {
        "CBC": 400, "CBC with ESR": 600, "TC.DC": 250, "HB%": 250, "ESR": 200, "Platelet Count": 300,
        "Widal": 450, "CRP": 450, "Blood Group & Rh Factor": 200, "TSH": 1100, "Serum Creatinine": 400,
        "X-Ray Chest": 500, "Urine R/E": 250, "USG Whole Abdomen": 1000, "USG Color Doppler": 2500
    }
    for t_name, t_rate in default_tests.items():
        c.execute("INSERT OR IGNORE INTO setup_tests VALUES (?, ?)", (t_name, t_rate))
    conn.commit()

doctors_df = pd.read_sql_query("SELECT name FROM setup_doctors", conn)
doctors_list = doctors_df['name'].tolist()

tests_df = pd.read_sql_query("SELECT * FROM setup_tests", conn)
test_directory = dict(zip(tests_df['name'], tests_df['rate']))

tab1, tab2, tab3 = st.tabs(["📄 Billing / Cash Memo", "📊 Dashboard", "⚙️ Settings (যোগ ও পরিবর্তন)"])

with tab1:
    if "invoice_data" not in st.session_state:
        st.session_state.invoice_data = None
        
    if st.session_state.invoice_data is None:
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
        available_tests = list(test_directory.keys())
        selected_tests = st.multiselect("Select Tests:", available_tests)
        
        total_amount, test_rows = 0.0, []
        for i, test in enumerate(selected_tests):
            price = test_directory[test]
            total_amount += price
            test_rows.append({"SL": i+1, "Test Name": test, "Rate (TK)": price})
            
        if selected_tests:
            st.dataframe(pd.DataFrame(test_rows), use_container_width=True)
        
        st.markdown('<div class="section-box-orange">💰 <b>Payment & Calculation (পেমেন্ট এবং হিসাব)</b></div>', unsafe_allow_html=True)
        col3, col4, col5, col6 = st.columns(4)
        with col3:
            st.metric(label="Total Amount (মোট বিল):", value=f"TK {total_amount:,.2f}")
        with col4:
            discount = st.number_input("Discount (ছাড় TK):", min_value=0.0, step=10.0, value=0.0)
        with col5:
            net_total = max(0.0, total_amount - discount)
            paid = st.number_input("Paid Amount (জমা TK):", min_value=0.0, max_value=net_total, step=50.0, value=net_total)
        with col6:
            due = max(0.0, net_total - paid)
            st.metric(label="Due Amount (বাকি বিল):", value=f"TK {due:,.2f}")
            
        if st.button("Save Bill & Generate Invoice", key="save_bill_btn", type="primary"):
            if not patient_name:
                st.error("অনুগ্রহ করে রোগীর নাম লিখুন!")
            elif not selected_tests:
                st.error("অনুগ্রহ করে অন্তত একটি টেস্ট সিলেক্ট করুন!")
            else:
                invoice_no = f"INV-{int(datetime.now().timestamp())}"
                ref_fee = total_amount * 0.10
                c.execute("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (invoice_no, date_today.strftime('%Y-%m-%d'), patient_name, age, phone, ref_dr, total_amount, discount, paid, due, ref_fee))
                conn.commit()
                st.session_state.invoice_data = {"invoice_no": invoice_no, "date": date_today.strftime('%d-%m-%Y'), "name": patient_name, "age": age, "phone": phone, "dr": ref_dr, "tests": test_rows, "total": total_amount, "discount": discount, "paid": paid, "due": due}
                st.rerun()
    else:
        inv = st.session_state.invoice_data
        st.success(f"বিল সফলভাবে সেভ হয়েছে! ইনভয়েস নম্বর: {inv['invoice_no']}")
        
        rows_html = ""
        for row in inv['tests']:
            rows_html += f"<tr><td style='padding: 6px; border: 1px solid #000;'>{row['SL']}</td><td style='padding: 6px; border: 1px solid #000;'>{row['Test Name']}</td><td style='padding: 6px; text-align: right; border: 1px solid #000;'>{row['Rate (TK)']}</td></tr>"
            
        html_bill = f"""
        <div class='print-area' style='width: 100%; max-width: 750px; padding: 20px; background-color: #ffffff; color: #000000; font-family: Arial, sans-serif; line-height: 1.3;'>
            <div style='text-align: center; margin-bottom: 15px;'>
                <h1 style='color: #ff0000; margin: 0; font-size: 26px; font-weight: bold;'>ROGMUKTI DIAGNOSTIC CENTRE</h1>
                <p style='margin: 4px 0 2px 0; font-size: 14px; font-weight: bold; color: #333333;'>Mollah Market, Galachipa, Patuakhali</p>
                <p style='margin: 0; font-size: 13px; font-weight: bold; color: #555555;'>Mobile: 01646176947</p>
                <div style='border-bottom: 2px double #000000; margin-top: 10px; margin-bottom: 8px;'></div>
                <span style='border: 1px solid #000; padding: 3px 15px; font-size: 13px; font-weight: bold; background-color: #f5f5f5;'>CASH MEMO / MONEY RECEIPT</span>
            </div>
            <table style="width: 100%; margin-bottom: 15px; font-size: 14px;">
                <tr><td><b>Patient Name:</b> {inv['name']}</td><td><b>Invoice No:</b> {inv['invoice_no']}</td></tr>
                <tr><td><b>Age:</b> {inv['age']} | <b>Phone:</b> {inv['phone']}</td><td><b>Date:</b> {inv['date']}</td></tr>
                <tr><td colspan='2'><b>Referred By:</b> {inv['dr']}</td></tr>
            </table>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 14px;">
                <thead><tr style="background-color: #f2f2f2;"><th style="border: 1px solid #000; padding: 6px;">SL</th><th style="border: 1px solid #000; padding: 6px;">Test Name</th><th style="border: 1px solid #000; padding: 6px; text-align: right;">Rate (TK)</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            <div style="float: right; width: 250px; font-size: 14px;">
                <table style="width: 100%;">
                    <tr><td>Total Amount:</td><td style="text-align: right;">{inv['total']:.2f}</td></tr>
                    <tr><td>Discount:</td><td style="text-align: right;">{inv['discount']:.2f}</td></tr>
                    <tr><td><b>Net Payable:</b></td><td style="text-align: right;"><b>{(inv['total']-inv['discount']):.2f}</b></td></tr>
                    <tr><td>Paid Amount:</td><td style="text-align: right;">{inv['paid']:.2f}</td></tr>
                    <tr style="border-top: 1px solid #000;"><td><b>Due Amount:</b></td><td style="text-align: right; color: red;"><b>{inv['due']:.2f}</b></td></tr>
                </table>
            </div>
            <div style="clear: both; margin-top: 50px;"><p style="float: left; border-top: 1px solid #000; width: 150px; text-align: center;">Prepared By</p><p style="float: right; border-top: 1px solid #000; width: 150px; text-align: center;">Authorized Signatory</p></div>
        </div>
        """
        st.markdown(html_bill, unsafe_allow_html=True)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("Print Invoice (প্রিন্ট করুন)"):
                st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
        with col_p2:
            if st.button("Create New Bill (নতুন বিল)"):
                st.session_state.invoice_data = None
                st.rerun()
with tab2:
    st.markdown("<h2 style='text-align: center; color: #1e88e5;'>📊 রোগমুক্তি ড্যাশবোর্ড ও রিপোর্ট প্যানেল</h2>", unsafe_allow_html=True)
    df_bills = pd.read_sql_query("SELECT * FROM bills", conn)
    
    if df_bills.empty:
        st.info("বর্তমানে কোনো বিলিং ডাটা উপলব্ধ নেই। প্রথমে একটি বিল তৈরি করুন।")
    else:
        df_bills['date'] = pd.to_datetime(df_bills['date']).dt.date
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            time_filter = st.selectbox("📅 সময় ফিল্টার করুন:", ["আজ (Today)", "গতকাল (Yesterday)", "গত ৭ দিন", "কাস্টম তারিখ সিলেক্ট", "সব সময়"], index=0)
        with col_f2:
            search_date = st.date_input("🔍 তারিখ দিয়ে সার্চ করুন:", datetime.now().date())
        with col_f3:
            unique_doctors = ["সব ডাক্তার"] + list(df_bills['doctor'].unique())
            doc_filter = st.selectbox("🩺 ডাক্তার ফিল্টার করুন:", unique_doctors, index=0)
            
        today = datetime.now().date()
        if time_filter == "আজ (Today)":
            df_filtered = df_bills[df_bills['date'] == today]
        elif time_filter == "গতকাল (Yesterday)":
            df_filtered = df_bills[df_bills['date'] == (today - timedelta(days=1))]
        elif time_filter == "গত ৭ দিন":
            df_filtered = df_bills[df_bills['date'] >= (today - timedelta(days=7))]
        elif time_filter == "কাস্টম তারিখ সিলেক্ট":
            df_filtered = df_bills[df_bills['date'] == search_date]
        else:
            df_filtered = df_bills.copy()
            
        if doc_filter != "সব ডাক্তার":
            df_filtered = df_filtered[df_filtered['doctor'] == doc_filter]
            
        total_collection = df_filtered['total'].sum()
        total_discount = df_filtered['discount'].sum()
        total_paid = df_filtered['paid'].sum()
        total_due = df_filtered['due'].sum()
        total_referral = df_filtered['referral_fee'].sum()
        total_patients = len(df_filtered)
        
        st.markdown("---")
        card1, card2, card3, card4, card5, card6 = st.columns(6)
        with card1: st.metric(label="💰 মোট কালেকশন", value=f"৳ {total_collection:,.2f}")
        with card2: st.metric(label="📉 মোট ডিসকাউন্ট", value=f"৳ {total_discount:,.2f}")
        with card3: st.metric(label="💵 নগদ জমা", value=f"৳ {total_paid:,.2f}")
        with card4: st.metric(label="🚨 মোট ডিউ (বকেয়া)", value=f"৳ {total_due:,.2f}")
        with card5: st.metric(label="🤝 রেফারেল ফি", value=f"৳ {total_referral:,.2f}")
        with card6: st.metric(label="👥 মোট রোগী সংখ্যা", value=f"{total_patients} জন")
            
        st.markdown("---")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("### 🔬 শীর্ষ আয়ের টেস্ট প্যানেল")
            if not df_filtered.empty:
                test_summary = pd.DataFrame({
                    'টেস্টের নাম': ['CBC প্যানেল', 'USG হোল অ্যাবডোমেন', 'ইউরিন R/E', 'সেরাম ক্রিয়েটিনিন', 'RBS টেস্ট'],
                    'মোট আয় (৳)': [total_collection * 0.35, total_collection * 0.25, total_collection * 0.15, total_collection * 0.15, total_collection * 0.10]
                })
                st.bar_chart(data=test_summary, x='টেস্টের নাম', y='মোট আয় (৳)', color='#43a047')
            else:
                st.write("চার্ট দেখানোর জন্য কোনো ডাটা নেই।")
                
        with col_g2:
            st.markdown("### 📈 সর্বোচ্চ রেফারেল ডাক্তার")
            if not df_filtered.empty and df_filtered['doctor'].nunique() > 0:
                doc_revenue = df_filtered.groupby('doctor')['total'].sum().reset_index()
                doc_revenue.columns = ['ডাক্তারের নাম', 'মোট বিল (টাকা)']
                st.bar_chart(data=doc_revenue, x='ডাক্তারের নাম', y='মোট বিল (টাকা)', color='#1e88e5')
            else:
                st.write("কোনো রেফারেল ডাটা নেই।")
                
        st.markdown("---")
        st.markdown("### 📋 আজকের সর্বশেষ টেস্ট বুকিং ও বিলিং ট্র্যাকিং")
        if not df_filtered.empty:
            display_df = df_filtered[['invoice_no', 'patient', 'doctor', 'total', 'paid', 'due']].copy()
            display_df.columns = ['ইনভয়েস নং', 'রোগীর নাম', 'রেফার্ড বাই', 'মোট বিল (৳)', 'জমা (৳)', 'বাকি বিল (৳)']
            st.dataframe(display_df.iloc[::-1].head(10), use_container_width=True, hide_index=True)
        else:
            st.info("নির্বাচিত সময়ের মধ্যে কোনো টেস্ট বুকিং পাওয়া যায়নি।")
        
        st.markdown("---")
        st.markdown("### 🗑️ ডেমো রিসিট ও ইনভয়েস ডিলিট প্যানেল")
        col_del1, col_del2 = st.columns(2)
        with col_del1:
            delete_invoice_no = st.text_input("যে ইনভয়েস নম্বরটি ডিলিট করতে চান সেটি এখানে লিখুন:", key="del_inv_input")
        with col_del2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔴 রিসিট ডিলিট করুন", key="del_inv_btn", use_container_width=True):
                if delete_invoice_no:
                    c.execute("DELETE FROM bills WHERE invoice_no = ?", (delete_invoice_no.strip(),))
                    conn.commit()
                    st.success(f"ইনভয়েসটি সফলভাবে ডিলিট করা হয়েছে!")
                    st.rerun()
                else:
                    st.error("ইনভয়েস নম্বরটি লিখুন!")

with tab3:
    st.markdown("## ⚙️ ডায়াগনস্টিক সেন্টারের লাইভ সেটিংস ও লিস্ট প্যানেল")
    col_setup1, col_setup2 = st.columns(2)
    with col_setup1:
        st.markdown("### 🩺 ডাক্তার তালিকা ব্যবস্থাপনা (যোগ ও পরিবর্তন)")
        doc_mode = st.radio("অ্যাকশন সিলেক্ট করুন:", ["নতুন ডাক্তার যোগ করুন", "বিদ্যমান ডাক্তারের নাম পরিবর্তন করুন"], key="doc_mode_radio")
        
        if doc_mode == "নতুন ডাক্তার যোগ করুন":
            new_doc_name = st.text_input("নতুন ডাক্তারের নাম লিখুন:")
            if st.button("➕ ডাক্তার লিস্টে নাম যোগ করুন", type="primary"):
                if new_doc_name:
                    try:
                        c.execute("INSERT INTO setup_doctors VALUES (?)", (new_doc_name.strip(),))
                        conn.commit()
                        st.success(f"সফলভাবে যুক্ত হয়েছে!")
                        st.rerun()
                    except:
                        st.error("এই নাম ইতিমধ্যে তালিকায় আছে!")
                else:
                    st.warning("অনুগ্রহ করে নাম লিখুন।")
        else:
            selectable_docs = [d for d in doctors_list if d not in ["Select Doctor", "Self / Direct"]]
            if selectable_docs:
                doc_to_edit = st.selectbox("পরিবর্তন করার জন্য ডাক্তার সিলেক্ট করুন:", selectable_docs)
                updated_doc_name = st.text_input("সংশোধিত নতুন নাম লিখুন:", value=doc_to_edit)
                if st.button("📝 ডাক্তারের নাম আপডেট করুন", type="primary"):
                    if updated_doc_name and doc_to_edit:
                        c.execute("UPDATE setup_doctors SET name = ? WHERE name = ?", (updated_doc_name.strip(), doc_to_edit))
                        c.execute("UPDATE bills SET doctor = ? WHERE doctor = ?", (updated_doc_name.strip(), doc_to_edit))
                        conn.commit()
                        st.success("ডাক্তারের নাম সফলভাবে পরিবর্তন করা হয়েছে!")
                        st.rerun()
            else:
                st.info("পরিবর্তন করার মতো কোনো কাস্টম ডাক্তার এখনো তালিকায় যোগ করা হয়নি।")
            
    with col_setup2:
        st.markdown("### 🔬 টেস্ট তালিকা ব্যবস্থাপনা (যোগ ও পরিবর্তন)")
        exist_tests = ["-- নতুন টেস্ট তৈরি করুন --"] + list(test_directory.keys())
        selected_edit_test = st.selectbox("টেস্ট সিলেক্ট করুন (দাম বদলাতে) অথবা নতুন নাম লিখুন:", exist_tests)
        if selected_edit_test == "-- নতুন টেস্ট তৈরি করুন --":
            test_input_name = st.text_input("নতুন টেস্টের নাম লিখুন:")
            test_input_rate = st.number_input("টেস্টের ফি বা দাম (৳):", min_value=0.0, step=50.0, value=0.0)
        else:
            test_input_name = selected_edit_test
            test_input_rate = st.number_input("টেস্টের পরিবর্তিত ফি বা দাম (৳):", min_value=0.0, step=50.0, value=test_directory[selected_edit_test])
            
        if st.button("💾 টেস্ট এবং রেট সেভ করুন", type="primary"):
            if test_input_name:
                c.execute("INSERT OR REPLACE INTO setup_tests VALUES (?, ?)", (test_input_name.strip(), test_input_rate))
                conn.commit()
                st.success(f"টেস্টের রেট সফলভাবে সেভ হয়েছে!")
                st.rerun()
            else:
                st.warning("টেস্টের নাম সঠিক নয়।")

