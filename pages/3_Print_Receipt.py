import streamlit as st
import sqlite3

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

st.title("🖨️ মানি রিসিট ও প্রিন্ট সেকশন")

conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# ডাটাবেজের সর্বশেষ সেভ হওয়া বিলের আইডি তুলে আনা
c.execute("SELECT MAX(id) FROM billing_records")
last_id_result = c.fetchone()
invoice_id = last_id_result[0] if last_id_result and last_id_result[0] else None

if invoice_id:
    # 📌 কুয়েরির এররটি এখানে নিখুঁতভাবে ফিক্স করা হয়েছে
    c.execute("SELECT * FROM billing_records WHERE id = ?", (invoice_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        name = row[1]
        age = row[2]
        phone = row[3]
        doctor = row[4]
        selected_tests_data = row[5]
        total_amount = float(row[6])
        discount_pct = float(row[7])
        advance_paid = float(row[8])
        due_amount = float(row[9])
        current_date = row[10]
        
        discount_amount = (total_amount * discount_pct) / 100.0

        st.components.v1.html("""
            <button onclick="parent.window.print()" style="
                background-color: #1a365d; color: white; padding: 12px 30px; 
                border: none; border-radius: 5px; font-size: 16px; 
                cursor: pointer; font-weight: bold; width: 100%;
            ">🖨️ রিসিট প্রিন্ট বা পিডিএফ সেভ করুন (Print Now)</button>
        """, height=60)
        
        st.markdown("""
        <style>
            @media print {
                body * { visibility: hidden; }
                #print-area, #print-area * { visibility: visible; }
                #print-area { position: absolute; left: 5mm; top: 5mm; width: 190mm; box-shadow: none; margin: 0; padding: 0; }
                @page { size: A4 portrait; margin: 10mm; }
            }
            .receipt-container { border: 1px solid #1a365d; padding: 20px; border-radius: 6px; background-color: #ffffff; color: #000000; margin-top: 15px; font-family: Arial, sans-serif; max-width: 700px; margin-left: auto; margin-right: auto; }
            .receipt-header { text-align: center; background-color: #1a365d; color: #ffffff; padding: 12px; border-radius: 4px; margin-bottom: 15px; }
            .info-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 13px; }
            .test-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 13px; }
            .test-table th, .test-table td { border: 1px solid #dddddd; padding: 8px; text-align: left; color: #000000; }
            .test-table th { background-color: #3182ce; color: #ffffff; }
            .summary-text { text-align: right; font-size: 14px; line-height: 1.5; color: #000000; }
        </style>
        """, unsafe_allow_html=True)
        
        table_rows = ""
        for item in selected_tests_data.split("|"):
            if ":" in item:
                t_name, t_price = item.split(":", 1)
                try: t_price_val = float(t_price)
                except: t_price_val = 0.0
                table_rows += f"<tr><td style='color: black;'>{t_name.strip()}</td><td style='text-align: right; color: black;'>{t_price_val:.2f} ৳</td></tr>"
            
        receipt_body = f"""
        <div id="print-area" class="receipt-container">
            <div class="receipt-header">
                <h1 style="margin: 0; font-size: 22px; color: white; letter-spacing: 0.5px;">ROG MUKTI DIAGNOSTIC CENTRE</h1>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: white;">Mollah Stand, Auliapur, Patuakhali &nbsp;|&nbsp; Phone: 01711867637</p>
            </div>
            <table class="info-table">
                <tr>
                    <td style="padding: 4px; color: black; width: 50%;"><b>Bill No:</b> #{invoice_id}</td>
                    <td style="padding: 4px; text-align: right; color: black; width: 50%;"><b>Date:</b> {current_date}</td>
                </tr>
                <tr>
                    <td style="padding: 4px; color: black;"><b>Patient Name:</b> {name}</td>
                    <td style="padding: 4px; text-align: right; color: black;"><b>Age:</b> {age} Years</td>
                </tr>
                <tr>
                    <td style="padding: 4px; color: black;"><b>Phone Number:</b> {phone}</td>
                    <td style="padding: 4px; text-align: right; color: black;"><b>Refd By:</b> {doctor}</td>
                </tr>
            </table>
            <table class="test-table">
                <thead>
                    <tr>
                        <th style="color: white; width: 70%;">Description (Test Name)</th>
                        <th style="text-align: right; color: white; width: 30%;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            <div class="summary-text">
                <p style="margin: 3px 0; color: black;"><b>Total Amount:</b> {total_amount:.2f} ৳</p>
                <p style="margin: 3px 0; color: black;"><b>Discount ({discount_pct:.1f}%):</b> -{discount_amount:.2f} ৳</p>
                <p style="margin: 3px 0; color: black;"><b>Advance Paid:</b> {advance_paid:.2f} ৳</p>
                <p style="color: red; font-size: 18px; margin: 8px 0 0 0;"><b>Due (বাকি টাকা): {due_amount:.2f} ৳</b></p>
            </div>
        </div>
        """
        st.markdown(receipt_body, unsafe_allow_html=True)
    else:
        st.error("কোনো বিলের তথ্য পাওয়া যায়নি।")
else:
    conn.close()
    st.info("ℹ️ কোনো বিল তৈরি করা হয়নি। প্রথমে 'Patient Entry' পেজ থেকে বিল সেভ করুন।")
