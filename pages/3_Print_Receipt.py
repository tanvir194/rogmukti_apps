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
        name, age, phone, doctor, selected_tests, total_fee, discount_pct, advance_paid, due_amount, current_date = row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]
        discount_amount = (total_fee * discount_pct) / 100.0
        tests_list = selected_tests.split(", ")

        # প্রিন্ট বাটন
        st.markdown("""
            <button onclick="window.print()" style="
                background-color: #2f855a; color: white; padding: 12px 30px; 
                border: none; border-radius: 5px; font-size: 16px; 
                cursor: pointer; font-weight: bold; margin-bottom: 20px;
            ">🖨️ রিসিট প্রিন্ট করুন (Print / Save PDF)</button>
        """, unsafe_allow_html=True)
        
        # মানি রিসিট ডিজাইন এবং প্রিন্ট সিএসএস
        receipt_html = f"""
        <style>
            @media print {{
                body * {{ visibility: hidden; }}
                #print-area, #print-area * {{ visibility: visible; }}
                #print-area {{ position: absolute; left: 0; top: 0; width: 100%; }}
            }}
        </style>
        <div id="print-area" style="border: 2px solid #1a365d; padding: 20px; border-radius: 10px; font-family: sans-serif; background-color: white; color: black;">
            <div style="text-align: center; background-color: #1a365d; color: white; padding: 10px; border-radius: 5px;">
                <h2>ROG MUKTI DIAGNOSTIC CENTRE</h2>
                <p>Mollah Stand, Auliapur, Patuakhali<br>Phone: 01711867637</p>
            </div>
            <div style="margin-top: 15px; display: flex; justify-content: space-between;">
                <div>
                    <p><b>Bill No:</b> #{invoice_id}</p>
                    <p><b>Patient Name:</b> {name}</p>
                    <p><b>Phone Number:</b> {phone}</p>
                </div>
                <div style="text-align: right;">
                    <p><b>Date:</b> {current_date}</p>
                    <p><b>Age:</b> {age} Years</p>
                    <p><b>Refd By:</b> {doctor}</p>
                </div>
            </div>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr style="background-color: #3182ce; color: white; text-align: left;">
                    <th style="padding: 8px;">Description (Test Name)</th>
                    <th style="padding: 8px; text-align: right;">Amount</th>
                </tr>
                {"".join([f"<tr><td style='padding: 8px; border-bottom: 1px solid #ddd; color: black;'>{t}</td><td style='padding: 8px; border-bottom: 1px solid #ddd; text-align: right; color: black;'>৳</td></tr>" for t in tests_list])}
            </table>
            <div style="margin-top: 20px; text-align: right; font-size: 16px;">
                <p><b>Total Amount:</b> {total_fee} ৳</p>
                <p><b>Discount ({discount_pct}%):</b> -{discount_amount} ৳</p>
                <p><b>Advance Paid:</b> {advance_paid} ৳</p>
                <p style="color: red; font-size: 18px;"><b>Due (বাকি টাকা): {due_amount} ৳</b></p>
            </div>
        </div>
        """
        st.markdown(receipt_html, unsafe_allow_html=True)
    else:
        st.error("কোনো বিলের তথ্য পাওয়া যায়নি।")
else:
    st.info("ℹ️ কোনো বিল তৈরি করা হয়নি। প্রথমে 'Patient Entry' পেজ থেকে বিল সেভ করুন।")
      
