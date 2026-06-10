import streamlit as st
import sqlite3

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

st.title("🖨️ মানি রিসিট ও প্রিন্ট সেকশন")

conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

c.execute("SELECT MAX(id) FROM billing_records")
last_id_result = c.fetchone()
invoice_id = last_id_result if last_id_result and last_id_result else None

if invoice_id:
    c.execute("SELECT * FROM billing_records WHERE id = ?", (invoice_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        name = row
        age = row
        phone = row
        doctor = row
        selected_tests_data = row
        total_amount = float(row)
        discount_pct = float(row)
        advance_paid = float(row)
        due_amount = float(row)
        current_date = row
        
        discount_amount = (total_amount * discount_pct) / 100.0
        due_amount = total_amount - discount_amount - advance_paid
        if due_amount < 0: due_amount = 0.0
        tests_list = selected_tests_data.split("|")

        st.components.v1.html("""
            <button onclick="parent.window.print()" style="
                background-color: #1a365d; color: white; padding: 12px 30px; 
                border: none; border-radius: 5px; font-size: 16px; 
                cursor: pointer; font-weight: bold; width: 100%;
            ">🖨️ রিসিট প্রিন্ট বা পিডিএফ সেভ করুন (Print Now)</button>
        """, height=60)
        
        # 📌 ৩. প্রিন্ট সাইজ বড় করার জন্য ফিক্সড সিএসএস (A4 এর ফুল প্রস্থ ব্যবহার করা হয়েছে)
        st.markdown("""
        <style>
            @media print {
                body * { visibility: hidden; }
                #print-area, #print-area * { visibility: visible; }
                #print-area { 
                    position: absolute; 
                    left: 0mm; 
                    top: 0mm; 
                    width: 100%; /* কাগজের পুরোটা জুড়ে বড় হবে */
                    box-shadow: none; 
                    margin: 0; 
                    padding: 0; 
                }
                @page { 
                    size: A4 portrait; 
                    margin: 15mm; /* চারপাশের মার্জিন স্ট্যান্ডার্ড করা হলো */
                }
            }
            .receipt-container { 
                border: 2px solid #1a365d; 
                padding: 30px; 
                border-radius: 8px; 
                background-color: #ffffff; 
                color: #000000; 
                margin-top: 15px; 
                font-family: Arial, sans-serif; 
                max-width: 850px; /* স্ক্রিনে এবং পেজে চওড়া দেখাবে */
                margin-left: auto; 
                margin-right: auto; 
            }
            .receipt-header { text-align: center; background-color: #1a365d; color: #ffffff; padding: 20px; border-radius: 6px; margin-bottom: 25px; }
            .info-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 16px; line-height: 1.8; }
            .test-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 16px; }
            .test-table th, .test-table td { border: 1px solid #dddddd; padding: 12px; text-align: left; color: #000000; }
            .test-table th { background-color: #3182ce; color: #ffffff; font-size: 17px; }
            .summary-text { text-align: right; font-size: 18px; line-height: 1.8; color: #000000; margin-top: 20px; }
        </style>
        """, unsafe_allow_html=True)
        
        table_rows = ""
        for item in tests_list:
            if ":" in item:
                t_name, t_price = item.split(":", 1)
                try: t_price_val = float(t_price)
                except: t_price_val = 0.0
                table_rows += f"<tr><td style='color: black; font-weight: bold;'>{t_name.strip()}</td><td style='text-align: right; color: black; font-weight: bold;'>{t_price_val:.2f} ৳</td></tr>"
            
        receipt_body = f"""
        <div id="print-area" class="receipt-container">
            <div class="receipt-header">
                <h1 style="margin: 0; font-size: 30px; color: white; letter-spacing: 1px; font-weight: bold;">ROG MUKTI DIAGNOSTIC CENTRE</h1>
                <p style="margin: 8px 0 0 0; font-size: 15px; color: white;">Mollah Stand, Auliapur, Patuakhali &nbsp;|&nbsp; Phone: 01711867637</p>
            </div>
            <table class="info-table">
                <tr>
                    <td style="padding: 6px; color: black; width: 50%; font-size: 16px;"><b>Bill No:</b> #{invoice_id}</td>
                    <td style="padding: 6px; text-align: right; color: black; width: 50%; font-size: 16px;"><b>Date:</b> {current_date}</td>
                </tr>
                <tr>
                    <td style="padding: 6px; color: black; font-size: 16px;"><b>Patient Name:</b> {name}</td>
                    <td style="padding: 6px; text-align: right; color: black; font-size: 16px;"><b>Age:</b> {age} Years</td>
                </tr>
                <tr>
                    <td style="padding: 6px; color: black; font-size: 16px;"><b>Phone Number:</b> {phone}</td>
                    <td style="padding: 4px; text-align: right; color: black; font-size: 16px;"><b>Refd By:</b> {doctor}</td>
                </tr>
            </table>
            <table class="test-table">
                <thead>
                    <tr>
                        <th style="color: white; width: 70%; font-weight: bold;">Description (Test Name)</th>
                        <th style="text-align: right; color: white; width: 30%; font-weight: bold;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            <div class="summary-text">
                <p style="margin: 5px 0; color: black;">Total Amount: <b>{total_amount:.2f} ৳</b></p>
                <p style="margin: 5px 0; color: black;">Discount ({discount_pct:.1f}%): <b>-{discount_amount:.2f} ৳</b></p>
                <p style="margin: 5px 0; color: black;">Advance Paid: <b>{advance_paid:.2f} ৳</b></p>
                <p style="color: red; font-size: 22px; margin: 12px 0 0 0; border-top: 2px solid #1a365d; padding-top: 10px;"><b>Due (বাকি টাকা): {due_amount:.2f} ৳</b></p>
            </div>
        </div>
        """
        st.markdown(receipt_body, unsafe_allow_html=True)
    else:
        st.error("কোনো বিলের তথ্য পাওয়া যায়নি।")
else:
    st.info("ℹ️ কোনো বিল তৈরি করা হয়নি। প্রথমে 'Patient Entry' পেজ থেকে বিল সেভ করুন।")
