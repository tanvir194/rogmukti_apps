import streamlit as st
import sqlite3

# ১. সিকিউরিটি চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

st.title("🖨️ মানি রিসিট ও প্রিন্ট সেকশন (A4 Size)")

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
        # ডাটাবেজের সঠিক ইনডেক্স অনুযায়ী ডেটা অ্যাসাইন করা
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

        # ২. প্রিন্ট মেকানিজম বাটন (যা সরাসরি ব্রাউজারের প্রিন্ট অপশন ওপেন করবে)
        st.components.v1.html("""
            <button onclick="parent.window.print()" style="
                background-color: #1a365d; 
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
        
        # ৩. প্রিন্ট করার সহজ সিএসএস
        st.markdown("""
        <style>
            @media print {
                body * { visibility: hidden; }
                #print-area, #print-area * { visibility: visible; }
                #print-area { position: absolute; left: 0; top: 0; width: 100%; }
            }
            .receipt-container {
                border: 2px solid #1a365d;
                padding: 30px;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
                margin-top: 15px;
                font-family: Arial, sans-serif;
            }
            .receipt-header {
                text-align: center;
                background-color: #1a365d;
                color: #ffffff;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .info-table, .test-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                color: #000000;
            }
            .test-table th, .test-table td {
                border: 1px solid #dddddd;
                padding: 10px;
                text-align: left;
            }
            .test-table th {
                background-color: #3182ce;
                color: #ffffff;
            }
            .summary-text {
                text-align: right;
                font-size: 16px;
                line-height: 1.6;
                color: #000000;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # ৪. স্ক্রিনের আসল মানি রিসিট বডি (সব ফাঁকা লাইন মুছে কম্প্যাক্ট করা হয়েছে)
        receipt_body = f"""
        <div id="print-area" class="receipt-container">
            <div class="receipt-header">
                <h1 style="margin: 0; font-size: 24px; color: white;">ROG MUKTI DIAGNOSTIC CENTRE</h1>
                <p style="margin: 5px 0 0 0; font-size: 14px; color: white;">Mollah Stand, Auliapur, Patuakhali<br>Phone: 01711867637</p>
            </div>
            <table class="info-table">
                <tr>
                    <td style="padding: 5px; color: black;"><b>Bill No:</b> #{invoice_id}</td>
                    <td style="padding: 5px; text-align: right; color: black;"><b>Date:</b> {current_date}</td>
                </tr>
                <tr>
                    <td style="padding: 5px; color: black;"><b>Patient Name:</b> {name}</td>
                    <td style="padding: 5px; text-align: right; color: black;"><b>Age:</b> {age} Years</td>
                </tr>
                <tr>
                    <td style="padding: 5px; color: black;"><b>Phone Number:</b> {phone}</td>
                    <td style="padding: 5px; text-align: right; color: black;"><b>Refd By:</b> {doctor}</td>
                </tr>
            </table>
            <table class="test-table">
                <thead>
                    <tr>
                        <th style="color: white;">Description (Test Name)</th>
                        <th style="text-align: right; color: white;">Amount</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for t in tests_list:
            receipt_body += f"<tr><td style='color: black;'>{t}</td><td style='text-align: right; color: black;'>- ৳</td></tr>"
            
        receipt_body += f"""
                </tbody>
            </table>
            <div class="summary-text">
                <p style="margin: 4px 0; color: black;"><b>Total Amount:</b> {total_fee} ৳</p>
                <p style="margin: 4px 0; color: black;"><b>Discount ({discount_pct}%):</b> -{discount_amount} ৳</p>
                <p style="margin: 4px 0; color: black;"><b>Advance Paid:</b> {advance_paid} ৳</p>
                <p style="color: red; font-size: 20px; margin: 10px 0 0 0;"><b>Due (বাকি টাকা): {due_amount} ৳</b></p>
            </div>
        </div>
        """
        
        st.markdown(receipt_body, unsafe_allow_html=True)
    else:
        st.error("কোনো বিলের তথ্য পাওয়া যায়নি।")
else:
    st.info("ℹ️ কোনো বিল তৈরি করা হয়নি। প্রথমে 'Patient Entry' পেজ থেকে বিল সেভ করুন।")
