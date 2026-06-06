import pandas as pd

def render_dashboard(st, conn, c):
    st.title("📊 Rogmukti Dashboard & Report Panel")
    df_bills = pd.read_sql_query("SELECT * FROM bills", conn)
    if not df_bills.empty:
        total_coll = df_bills['net_amount'].sum() if 'net_amount' in df_bills.columns else (df_bills['total_amount'].sum() if 'total_amount' in df_bills.columns else 0)
        total_paid = df_bills['paid_amount'].sum() if 'paid_amount' in df_bills.columns else (df_bills['paid'].sum() if 'paid' in df_bills.columns else 0)
        total_due = df_bills['due_amount'].sum() if 'due_amount' in df_bills.columns else (df_bills['due'].sum() if 'due' in df_bills.columns else 0)
        total_pat = len(df_bills)
    else:
        total_coll = total_paid = total_due = total_pat = 0
        
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Collection", f"৳ {total_coll:,.2f}")
    c2.metric("Cash Received", f"৳ {total_paid:,.2f}")
    c3.metric("Total Due", f"৳ {total_due:,.2f}")
    c4.metric("Total Patients", f"{total_pat} Persons")
    
    st.markdown("---")
    st.subheader("📋 Latest Invoice & Billing Tracking (Sorted)")
    df_table = pd.read_sql_query("SELECT * FROM bills ORDER BY invoice_no DESC", conn)
    if not df_table.empty:
        p_col = 'patient_name' if 'patient_name' in df_table.columns else ('name' if 'name' in df_table.columns else df_table.columns[0])
        cols = [col for col in ['invoice_no', p_col, 'total_amount', 'paid_amount', 'due_amount', 'paid', 'due', 'tests'] if col in df_table.columns]
        st.dataframe(df_table[cols], use_container_width=True)

def render_billing(st, conn, c, FPDF, datetime):
    st.title("💳 Create New Patient Bill & Memo")
    if 'last_saved_memo' not in st.session_state: 
        st.session_state['last_saved_memo'] = None
        
    with st.form(key='billing_form'):
        gen_invoice = f"INV-{int(datetime.now().timestamp())}"
        st.write(f"### Invoice No: {gen_invoice}")
        
        pat_name = st.text_input("Patient Full Name *")
        pat_phone = st.text_input("Mobile Number")
        pat_age = st.text_input("Age")
        pat_gender = st.selectbox("Gender", ["Male", "Female", "Others"])
        
        test_catalogue = {
            "CBC (Complete Blood Count)": 400,
            "Blood Grouping & Rh Factor": 200,
            "Serum Creatinine": 300,
            "HBsAg (Hepatitis B)": 350,
            "Lipid Profile": 1000,
            "USG of Whole Abdomen": 1200,
            "Memory Test (Custom)": 500
        }
        selected_tests = st.multiselect("Select Tests:", list(test_catalogue.keys()))
        
        total_bill = sum([test_catalogue[t] for t in selected_tests])
        st.write(f"### Total Bill: ৳ {total_bill}")
        
        disc_val = st.number_input("Discount (৳)", min_value=0, max_value=total_bill if total_bill > 0 else 0, value=0)
        payable_net = total_bill - disc_val
        paid_val = st.number_input("Paid Amount (৳)", min_value=0, max_value=payable_net if payable_net > 0 else 0, value=0)
        due_val = payable_net - paid_val
        st.write(f"#### Remaining Due: ৳ {due_val}")
        
        tests_string = ", ".join([f"{t} (৳{test_catalogue[t]})" for t in selected_tests])
        
        if st.form_submit_button("💾 Save Bill & Generate Memo"):
            if pat_name and selected_tests:
                cur_date = datetime.now().strftime("%Y/%m/%d")
                try:
                    c.execute("INSERT INTO bills (invoice_no, date, patient_name, age, gender, phone, total_amount, discount, net_amount, paid_amount, due_amount, tests) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", 
                              (gen_invoice, cur_date, pat_name, pat_age, pat_gender, pat_phone, total_bill, disc_val, payable_net, paid_val, due_val, tests_string))
                except:
                    c.execute("INSERT INTO bills (invoice_no, total_amount, paid, due) VALUES (?,?,?,?)", (gen_invoice, total_bill, paid_val, due_val))
                conn.commit()
                st.session_state['last_saved_memo'] = {"inv": gen_invoice, "name": pat_name, "tests": tests_string, "total": total_bill, "paid": paid_val, "due": due_val, "disc": disc_val, "phone": pat_phone, "age": pat_age, "gender": pat_gender}
                st.success("🎉 Bill Saved Successfully!")
                st.rerun()
                
    if st.session_state['last_saved_memo'] is not None:
        m = st.session_state['last_saved_memo']
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 10, "ROGMUKTI DIAGNOSTIC CENTRE", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, f"Invoice No: {m['inv']} | Patient: {m['name']} | Phone: {m['phone']}", ln=True, align="C")
        pdf.ln(5)
        pdf.cell(20, 8, "SL", border=1)
        pdf.cell(120, 8, "Test Name", border=1)
        pdf.cell(50, 8, "Price", border=1, ln=True)
        
        sl = 1
        for item in m["tests"].split(", "):
            t_name, t_pr = item.split(" (৳")
            pdf.cell(20, 8, str(sl), border=1)
            pdf.cell(120, 8, t_name, border=1)
            pdf.cell(50, 8, t_pr.replace(")", ""), border=1, ln=True)
            sl += 1
            
        pdf.ln(5)
        pdf.cell(140, 6, "Total Amount:", align="R"); pdf.cell(50, 6, f"{m['total']}.00 TK", ln=True, align="R")
        pdf.cell(140, 6, "Paid Cash:", align="R"); pdf.cell(50, 6, f"{m['paid']}.00 TK", ln=True, align="R")
        pdf.cell(140, 6, "Remaining Due:", align="R"); pdf.cell(50, 6, f"{m['due']}.00 TK", ln=True, align="R")
        pdf_bytes = pdf.output(dest="S")
        st.download_button(label="📥 DOWNLOAD A4 CASH MEMO (PDF)", data=pdf_bytes, file_name=f"Invoice_{m['inv']}.pdf", mime="application/pdf", use_container_width=True)
              
