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
    available_tests = [test for test in test_directory.keys() if test != "Select Test"]
    selected_tests = st.multiselect("Select Tests:", available_tests)
    total_amount, test_rows = 0.0, []
    for i, test in enumerate(selected_tests):
        price = test_directory[test]
        total_amount += price
        test_rows.append({"SL": i+1, "Test Name": test, "Rate (৳)": price})
    if selected_tests: st.dataframe(pd.DataFrame(test_rows), use_container_width=True)
    st.markdown('<div class="section-box-orange">💰 <b>Payment & Calculation (পেমেন্ট এবং হিসাব)</b></div>', unsafe_allow_html=True)
    col3, col4, col5, col6 = st.columns(4)
    with col3: st.metric(label="Total Amount (মোট বিল):", value=f"৳ {total_amount:,.2f}")
    with col4: discount = st.number_input("Discount (ছাড় ৳):", min_value=0.0, step=10.0, value=0.0)
    with col5:
        net_total = max(0.0, total_amount - discount)
        paid = st.number_input("Paid Amount (জমা ৳):", min_value=0.0, max_value=net_total, step=50.0, value=net_total)
    with col6:
        due = max(0.0, net_total - paid)
        st.metric(label="Due Amount (বাকি বিল):", value=f"৳ {due:,.2f}")
    if st.button("Save Bill & Generate Invoice", key="save_bill_btn", type="primary"):
        if not patient_name: st.error("অনুগ্রহ করে রোগীর নাম লিখুন!")
        elif not selected_tests: st.error("অনুগ্রহ করে অন্তত একটি টেস্ট সিলেক্ট করুন!")
        else:
            invoice_no = f"INV-{int(datetime.now().timestamp())}"
            ref_fee = total_amount * 0.30
            c.execute("INSERT INTO bills VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (invoice_no, date_today.strftime('%Y-%m-%d'), patient_name, age, phone, ref_dr, total_amount, discount, paid, due, ref_fee))
            conn.commit()
            st.success(f"বিল সফলভাবে সেভ হয়েছে! ইনভয়েস নম্বর: {invoice_no}")
            st.markdown("---")
            
            # মেমোর লেখার টেক্সট সুন্দরভাবে তৈরি করা যাতে ডাউনলোড বাটন ব্যবহার করতে পারে
            memo_txt = f"=== ROGMUKTI DIAGNOSTIC CENTRE ===\nMollah Market, Galachipa\nMobile: 01646176947\n--------------------------------\nInvoice No: {invoice_no}\nDate: {date_today.strftime('%d-%m-%Y')}\nPatient Name: {patient_name}\nAge: {age} | Phone: {phone}\nRef By: {ref_dr}\n--------------------------------\n"
            for row in test_rows: memo_txt += f"- {row['Test Name']}: ৳ {row['Rate (৳)']}\n"
            memo_txt += f"--------------------------------\nTotal Amount: ৳ {total_amount}\nDiscount: ৳ {discount}\nPaid Amount: ৳ {paid}\nDue Amount: ৳ {due}\n================================"

            st.html(f"<div style=\"border: 2px solid #000000; padding: 20px; background-color: #ffffff; color: #000000; font-family: 'Courier New', Courier, monospace;\"><div style=\"text-align: center; margin-bottom: 20px;\"><h1 style=\"color: #ff0000; margin: 0; font-size: 24px; font-weight: bold; letter-spacing: 1px;\">ROGMUKTI DIAGNOSTIC CENTRE</h1><p style=\"margin: 5px 0 2px 0; font-size: 14px; font-weight: bold; color: #333333;\">Mollah Market, Galachipa, Patuakhali</p><p style=\"margin: 0; font-size: 13px; font-weight: bold; color: #555555;\">Mobile: 01646176947</p><div style=\"border-bottom: 2px double #000000; margin-top: 10px; margin-bottom: 5px;\"></div><span style=\"background-color: #000000; color: #ffffff; padding: 3px 15px; font-size: 13px; font-weight: bold;\">CASH MEMO / MONEY RECEIPT</span></div><table style=\"width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 14px; color: #000000;\"><tr><td style=\"padding: 5px; width: 18%; font-weight: bold;\">Invoice No:</td><td style=\"padding: 5px; width: 32%; border-bottom: 1px dotted #000;\">{invoice_no}</td><td style=\"padding: 5px; width: 15%; font-weight: bold; text-align: right;\">Date:</td><td style=\"padding: 5px; width: 35%; border-bottom: 1px dotted #000; text-align: center;\">{date_today.strftime('%d-%m-%Y')}</td></tr><tr><td style=\"padding: 5px; font-weight: bold;\">Patient Name:</td><td style=\"padding: 5px; border-bottom: 1px dotted #000; font-weight: bold;\">{patient_name}</td><td style=\"padding: 5px; font-weight: bold; text-align: right;\">Age/Sex:</td><td style=\"padding: 5px; border-bottom: 1px dotted #000; text-align: center;\">{age}</td></tr><tr><td style=\"padding: 5px; font-weight: bold;\">Mobile No:</td><td style=\"padding: 5px; border-bottom: 1px dotted #000;\">{phone}</td><td style=\"padding: 5px; font-weight: bold; text-align: right;\">Ref. By:</td><td style=\"padding: 5px; border-bottom: 1px dotted #000; font-weight: bold; text-align: center;\">{ref_dr}</td></tr></table><div style=\"border-bottom: 1px solid #000000; margin-bottom: 10px;\"></div><p style=\"margin: 0; font-weight: bold; font-size: 14px;\">🔬 INVESTIGATION LIST (টেস্টের বিবরণ):</p></div>")
            st.dataframe(pd.DataFrame(test_rows), use_container_width=True)
            st.html(f"<div style=\"border: 2px solid #000000; border-top: none; padding: 15px; background-color: #ffffff; color: #000000; font-family: 'Courier New', Courier, monospace;\"><table style=\"width: 100%; font-size: 15px; font-weight: bold; border-collapse: collapse;\"><tr style=\"border-top: 1px solid #000; border-bottom: 1px solid #000;\"><td style=\"padding: 8px 5px; width: 25;\">Total: ৳ {total_amount}</td><td style=\"padding: 8px 5px; width: 25%; color: blue;\">Discount: ৳ {discount}</td><td style=\"padding: 8px 5px; width: 25%; color: green;\">Paid: ৳ {paid}</td><td style=\"padding: 8px 5px; width: 25%; color: red;\">Due: ৳ {due}</td></tr></table><div style=\"margin-top: 40px; display: flex; justify-content: space-between; font-size: 12px;\"><p style=\"border-top: 1px solid #000; width: 140px; text-align: center; margin: 0; color: #000000;\">Prepared By</p><p style=\"border-top: 1px solid #000; width: 140px; text-align: center; margin: 0; color: #000000;\">Authorized Signature</p></div></div><br>")
            
            # স্ট্রিমলিট-এর নিজস্ব ১ ক্লিকে ডাউনলোড বাটন যা মোবাইলে ১০০% কাজ করে
            st.download_button(label="📥 এই রসিদটি (Cash Memo) মোবাইলে ডাউনলোড করুন", data=memo_txt, file_name=f"Invoice_{invoice_no}.txt", mime="text/plain", use_container_width=True)
with tab2:
    st.header("📊 দৈনিক, साप्ताहिक ও মাসিক ড্যাশবোর্ড")
    try:
        df_dash = pd.read_sql_query("SELECT * FROM bills", conn)
        if not df_dash.empty:
            df_dash['date'] = pd.to_datetime(df_dash['date'], errors='coerce')
            f_opt = st.selectbox("হিসাব দেখার সময় নির্বাচন করুন", ["সব সময়", "আজ", "এই সপ্তাহ", "এই মাস"], key="dash_time_f_unique")
            t_now = datetime.today()
            if f_opt == "আজ": f_df = df_dash[df_dash['date'].dt.date == t_now.date()]
            elif f_opt == "এই সপ্তাহ": f_df = df_dash[df_dash['date'] >= (t_now - timedelta(days=t_now.weekday()))]
            elif f_opt == "এই মাস": f_df = df_dash[(df_dash['date'].dt.month == t_now.month) & (df_dash['date'].dt.year == t_now.year)]
            else: f_df = df_dash
            db_c1, db_c2, db_c3, db_c4 = st.columns(4)
            db_c1.metric("মোট কালেকশন", f"৳ {f_df['total'].sum() if 'total' in f_df else 0:,.2f}")
            db_c2.metric("মোট ডিসকাউন্ট", f"৳ {f_df['discount'].sum() if 'discount' in f_df else 0:,.2f}")
            db_c3.metric("মোট ডিউ (বাকি)", f"৳ {f_df['due'].sum() if 'due' in f_df else 0:,.2f}")
            db_c4.metric("মোট রেফারেল ফি (৩০%)", f"৳ {f_df['referral_fee'].sum() if 'referral_fee' in f_df else 0:,.2f}")
            st.subheader("👨‍⚕️ ডাক্তার ভিত্তিক রেফারেল রিপোর্ট (নামসহ)")
            av_cols = [col for col in ['doctor', 'patient', 'invoice_no', 'total', 'referral_fee', 'date'] if col in f_df]
            st.dataframe(f_df[av_cols], use_container_width=True)
            st.markdown('<button onclick="window.print()" style="background-color: #4CAF50; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold;">🖨️ এই ড্যাশবোর্ড রিপোর্টটি প্রিন্ট করুন</button>', unsafe_allow_html=True)
        else: st.info("ডেটাবেজে এখনো কোনো বিলের রেকর্ড নেই। একটি নতুন বিল সেভ করলেই ড্যাশবোর্ড সচল হয়ে যাবে।")
    except Exception as e: st.info("নতুন ডাটাবেজ তৈরি হচ্ছে। একটি নতুন বিল সেভ করলেই ড্যাশবোর্ড সচল হয়ে যাবে।")
    
