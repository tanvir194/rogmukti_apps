import sys
import os
import streamlit as st
import sqlite3

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Money Receipt", layout="wide")

st.title("🖨️ A4 Full Width Money Receipt")

# ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

default_invoice = st.session_state.get('last_invoice_id', 0)

col_search1, col_search2 = st.columns(2)
with col_search1:
    invoice_id = st.number_input("Enter Bill No / Invoice ID to Print:", min_value=0, value=int(default_invoice), step=1)

# ডাটাবেজ থেকে ডাটা কুয়েরি করা
c.execute("SELECT * FROM billing_records WHERE id=?", (invoice_id,))
record = c.fetchone()

if record:
    # 🛠️ ডাটাবেজের ইনডেক্স নম্বরগুলো সঠিকভাবে ঠিক করা হলো
    p_id = record[0]
    p_name = record[1]
    p_age = record[2]
    p_phone = record[3]
    p_doctor = record[4]
    p_tests_str = record[5]      
    total_bill = record[6]
    discount_tk = record[7]     
    advance_paid = record[8]
    due_amount = record[9]
    billing_date = record[10]

    st.write("")
    if st.button("🖨️ Print Money Receipt Now"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
    st.write("")

    # 📄 পুরো A4 পেজ জুড়ে ছড়িয়ে আসার জন্য টেবিল স্ট্রাকচার
    receipt_html = f"""
    <div style="width:100%; max-width:100%; font-family:Arial, sans-serif; color:#000000; padding:15px; box-sizing:border-box;">
        
        <!-- ডায়াগনস্টিক সেন্টারের হেডার -->
        <div style="text-align:center; border-bottom:3px double #000000; padding-bottom:15px; margin-bottom:20px;">
            <h1 style="font-size:32px; font-weight:bold; margin:0; color:#000000;">ROGMUKTI DIAGNOSTIC CENTRE</h1>
            <p style="font-size:15px; margin:5px 0 0 0;">Mollah stand, Auliapur, Patuakhali</p>
            <p style="font-size:16px; font-weight:bold; margin:3px 0 0 0;">Mobile: 01711867637</p>
        </div>
        
        <!-- পেশেন্ট ডিটেইলস টেবিল (ফুল এ৪ পেজ চওড়া) -->
        <table style="width:100%; font-size:16px; margin-bottom:25px; line-height:1.8;">
            <tr>
                <td style="width:50%;"><b>Invoice ID:</b> #{p_id}</td>
                <td style="text-align:right; width:50%;"><b>Date:</b> {billing_date}</td>
            </tr>
            <tr>
                <td><b>Patient Name:</b> {p_name}</td>
                <td style="text-align:right;"><b>Age:</b> {p_age} Y</td>
            </tr>
            <tr>
                <td><b>Mobile No:</b> {p_phone}</td>
                <td style="text-align:right;"><b>Ref. By:</b> {p_doctor}</td>
            </tr>
        </table>
        
        <div style="font-weight:bold; font-size:16px; border-bottom:2px solid #000000; padding-bottom:5px; margin-bottom:10px;">Test Description & Rate</div>
        
        <!-- মূল টেস্টের লিস্ট টেবিল -->
        <table style="width:100%; border-collapse:collapse; font-size:16px;">
            <thead>
                <tr style="background-color:#f2f2f2;">
                    <th style="width:10%; border:1px solid #000000; padding:10px; text-align:center;">SL</th>
                    <th style="width:65%; border:1px solid #000000; padding:10px; text-align:left;">Test Name</th>
                    <th style="width:25%; border:1px solid #000000; padding:10px; text-align:right;">Price</th>
                </tr>
            </thead>
            <tbody>
    """

    if p_tests_str:
        tests_list = p_tests_str.split(",")
    else:
        tests_list = []
        
    serial_no = 1
    for test_item in tests_list:
        test_item = test_item.strip()
        if not test_item:
            continue
            
        if "(" in test_item and ")" in test_item:
            # 🛠️ পাইথন লিস্ট ইনডেক্সিং এবার সম্পূর্ণ নির্ভুল করা হয়েছে
            parts = test_item.split("(")
            t_name = parts[0].strip()
            t_price = parts[1].replace(")", "").strip()
            try:
                t_price_formatted = f"{float(t_price):.2f}"
            except:
                t_price_formatted = t_price
        else:
            t_name = test_item
            t_price_formatted = "0.00"
            
        receipt_html += f"""
                <tr>
                    <td style="border:1px solid #000000; padding:10px; text-align:center;">{serial_no}</td>
                    <td style="border:1px solid #000000; padding:10px;">{t_name}</td>
                    <td style="border:1px solid #000000; padding:10px; text-align:right;">{t_price_formatted} Tk</td>
                </tr>
        """
        serial_no += 1

    try:
        t_bill = float(total_bill)
        d_tk = float(discount_tk)
        a_paid = float(advance_paid)
        d_amt = float(due_amount)
    except:
        t_bill, d_tk, a_paid, d_amt = 0.0, 0.0, 0.0, 0.0

    receipt_html += f"""
            </tbody>
        </table>
        
        <!-- ফাইনাল সামারি বক্স (ডান পাশে চওড়া বক্স আকারে) -->
        <table style="margin-top:25px; float:right; width:45%; font-size:16px; border:1px solid #000000; padding:15px; background-color:#f9f9f9; line-height:1.8; border-collapse:collapse;">
            <tr><td style="padding:5px;"><b>Total Bill:</b></td><td style="text-align:right; padding:5px;">{t_bill:.2f} Tk</td></tr>
            <tr><td style="padding:5px;"><b>Discount:</b></td><td style="text-align:right; padding:5px;">{d_tk:.2f} Tk</td></tr>
            <tr><td style="padding:5px;"><b>Advance Paid:</b></td><td style="text-align:right; padding:5px;">{a_paid:.2f} Tk</td></tr>
            <tr style="border-top:1px solid #000000; font-size:18px; color:#ff0000;"><td style="padding:5px;"><b>Due Amount:</b></td><td style="text-align:right; padding:5px;"><b>{d_amt:.2f} Tk</b></td></tr>
        </table>
        <div style="clear:both;"></div>
        
        <div style="text-align:center; margin-top:60px; font-size:14px; color:#555555; font-style:italic; border-top:1px dashed #000000; padding-top:15px;">
            Thank you for trusting us with your care.
        </div>
    </div>
    
    <style>
    @media print {
        header, [data-testid="stSidebar"], .stButton, .stNumberInput { display: none !important; }
        @page { size: A4; margin: 0mm; }
    }
    </style>
    """
    
    st.markdown(receipt_html, unsafe_allow_html=True)

else:
    if invoice_id > 0:
        st.error(f"🚨 দুঃখিত, #{invoice_id} নম্বরের কোনো বিল ডাটাবেজে খুঁজে পাওয়া যায়নি!")
    else:
        st.info("ℹ️ বিল প্রিন্ট করার জন্য উপরে সঠিক Invoice ID নম্বরটি ইনপুট দিন।")

conn.close()
