import streamlit as st
import sqlite3

# ১. সিকিউরিটি চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

st.title("🖨️ মানি রিসিট ও প্রিন্ট সেকশন")

# সেশন স্টেট থেকে সর্বশেষ সেভ হওয়া বিলের আইডি নেওয়া
if "last_invoice_id" in st.session_state:
    invoice_id = st.session_state.last_invoice_id
    
    # ডাটাবেজ থেকে ওই বিলের তথ্য তুলে আনা
    conn = sqlite3.connect("rogmukti_clinic_fix.db")
    c = conn.cursor()
    c.execute("SELECT * FROM billing_records WHERE id = ?", (invoice_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        # ডাটাবেজের কলামগুলো আলাদা করা
        name = row[1]
        age = row[2]
        phone = row[3]
        doctor = row[4]
        selected_tests = row[5]
        total_fee = row[6]
        discount_pct = row[7]
        advance_paid = row[8]
        due_amount = row[9]
        current_date = row[10]
        
        discount_amount = (total_fee * discount_pct) / 100.0
        tests_list = selected_tests.split(", ")

        # ২. প্রিন্ট মেকানিজম বাটন
        st.components.v1.html("""
            <button onclick="parent.window.print()" style="
                background-color: #2f855a; 
                color: white; 
                padding: 12px 30px; 
                border: none; 
                border-radius: 5px; 
                font-size: 16px; 
                cursor: pointer; 
                font-weight: bold;
                width: 100%;
            ">🖨️ রিসিট প্রিন্ট বা পিডিএফ সেভ করুন (Print Now)</button>
        """, height=60)
        
        # ৩. টেবিলের রো (Rows) তৈরি করার লজিক
        table_rows = ""
        for t in tests_list:
            table_rows += f"<tr><td style='padding: 6px; border: 1px solid #ddd; color: black;'>{t}</td><td style='padding: 6px; border: 1px solid #ddd; text-align: right; color: black;'>- ৳</td></tr>"
        
        # ৪. মানি রিসিট ডিজাইন এবং A4 এর অর্ধেকের (A5) সাইজ ফিক্স করার CSS
        receipt_html = f"""
        <style>
            @media print {{
                body * {{ visibility: hidden; }}
                #print-area, #print-area * {{ visibility: visible; }}
                #print-area {{ 
                    position: absolute; 
                    left: 0; 
                    top: 0; 
                    width: 148mm; 
                    max-height: 210mm; 
                    box-shadow: none;
                    margin: 0;
                    padding: 10px;
                }}
                @page {{
                    size: A5 portrait; 
                    margin: 0;
                }}
            }}
            .receipt-box {{
                border: 2px solid #1a365d; 
                padding: 20px; 
                border-radius: 10px; 
                font-family: sans-serif; 
                background-color: white; 
                color: black; 
                margin-top: 10px;
                max-width: 550px; 
            }}
        </style>
        
        <div id="print-area" class="receipt-box">
            <div style="text-align: center; background-color: #1a365d; color: white; padding: 10px; border-radius: 5px;">
                <h2 style="margin: 0; font-size: 20px;">ROG MUKTI DIAGNOSTIC CENTRE</h2>
                <p style="margin: 5px 0 0 0; font-size: 13px;">Mollah Stand, Auliapur, Patuakhali<br>Phone: 01711867637</p>
            </div>
            
            <div style="margin-top: 15px; display: flex; justify-content: space-between; font-size: 14px; line-height: 1.6; color: black;">
                <div>
                    <p style="margin: 0;"><b>Bill No:</b> #{invoice_id}</p>
                    <p style="margin: 0;"><b>Patient Name:</b> {name}</p>
                    <p style="margin: 0;"><b>Phone Number:</b> {phone}</p>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 0;"><b>Date:</b> {current_date}</p>
                    <p style="margin: 0;"><b>Age:</b> {age} Years</p>
                    <p style="margin: 0;"><b>Refd By:</b> {doctor}</p>
                </div>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px;">
                <tr style="background-color: #3182ce; color: white; text-align: left;">
                    <th style="padding: 6px; border: 1px solid #ddd;">Description (Test Name)</th>
                    <th style="padding: 6px; text-align: right; border: 1px solid #ddd;">Amount</th>
                </tr>
                {table_rows}
            </table>
            
            <div style="margin-top: 15px; text-align: right; font-size: 14px; line-height: 1.5; color: black;">
                <p style="margin: 3px 0;"><b>Total Amount:</b> {total_fee} ৳</p>
                <p style="margin: 3px 0;"><b>Discount ({discount_pct}%):</b> -{discount_amount} ৳</p>
                <p style="margin: 3px 0;"><b>Advance Paid:</b> {advance_paid} ৳</p>
                <p style="color: red; font-size: 16px; margin: 5px 0;"><b>Due (বাকি টাকা): {due_amount} ৳</b></p>
            </div>
        </div>
        """
        st.markdown(receipt_html, unsafe_allow_html=True)
    else:
        st.error("কোনো বিলের তথ্য পাওয়া যায়নি।")
else:
    st.info("ℹ️ কোনো বিল তৈরি করা হয়নি। প্রথমে 'Patient Entry' পেজ থেকে বিল সেভ করুন।")
