import sys
import os
import streamlit as st
import sqlite3

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Money Receipt", layout="wide")

# ২. কাস্টম ডার্ক মোড এবং রিসিটের প্রিমিয়াম হোয়ایت কার্ড CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0b131f !important;
        color: #e2e8f0 !important;
    }
    .stApp label {
        color: #38bdf8 !important;
        font-weight: 500 !important;
    }
    .stTextInput input {
        background-color: #18263c !important;
        color: #ffffff !important;
        border: 1px solid #2d3f5d !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    .stButton button {
        background-color: #0284c7 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        width: 100%;
    }
    
    /* 📄 স্ক্রিন ভিউ ডিজাইন */
    .receipt-container {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 12px;
        padding: 25px;
        max-width: 600px;
        margin: 0 auto;
        font-family: 'Segoe UI', Arial, sans-serif;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        border: 1px solid #cbd5e1;
    }
    .receipt-header {
        text-align: center;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .receipt-title {
        color: #1e3a8a !important;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }
    .receipt-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
    }
    .receipt-table th {
        background-color: #f1f5f9 !important;
        color: #1e3a8a !important;
        border-bottom: 2px solid #cbd5e1 !important;
        padding: 8px;
        text-align: left;
    }
    .receipt-table td {
        border-bottom: 1px solid #e2e8f0 !important;
        padding: 8px;
        color: #334155 !important;
    }
    .summary-text {
        text-align: right;
        font-size: 14px;
        margin-top: 4px;
        color: #1e293b !important;
    }
    
    /* 🖨️ প্রিন্ট করার সময় এই কাস্টম ডিজাইনটি চালু হবে */
    @media print {
        body * {
            visibility: hidden !important;
        }
        .receipt-container, .receipt-container * {
            visibility: visible !important;
        }
        
        /* 🖨️ রসিদটি কাগজের একদম উপরে ওঠানো এবং লম্বালম্বি সাইজ ছোট করার ফিক্স */
        .receipt-container {
            position: absolute !important;
            left: 15% !important; 
            top: 0 !important;
            width: 70% !important; 
            box-shadow: none !important;
            border: 1px solid #000000 !important;
            padding: 20px !important;
            margin-top: -15px !important; /* ওপরে চাপানোর জন্য মার্জিন */
            line-height: 1.2 !important;  /* রসিদের ফালতু লম্বা ভাব দূর করার জন্য */
        }
        
        .receipt-header {
            margin-bottom: 10px !important;
            padding-bottom: 5px !important;
        }
        
        /* টেস্ট টেবিলের লাইনের মাঝের ফালতু ফাঁকা জায়গা কমানো */
        .receipt-table {
            margin-top: 5px !important;
        }
        .receipt-table th {
            padding: 5px !important;
            font-size: 13px !important;
            background-color: #f1f5f9 !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
            border-bottom: 1px solid #000000 !important;
        }
        .receipt-table td {
            padding: 4px 5px !important; /* টেবিলের ঘরের উচ্চতা কমানো হলো */
            font-size: 13px !important;
            border-bottom: 1px solid #cbd5e1 !important;
        }
        .summary-text {
            margin-top: 2px !important;
            font-size: 13px !important;
        }
        
        @page {
            size: A4;
            margin-top: 5mm; /* কাগজের ওপরের ফাঁকা অংশ কমানো হলো */
            margin-bottom: 15mm;
            margin-left: 15mm;
            margin-right: 15mm;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🖨️ English Money Receipt")

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

    # HTML রিসিট জেনারেট করা (আপনার চাওয়া মোবাইল নম্বরটি এখানে সঠিকভাবে দেওয়া হয়েছে)
    receipt_html = f"""<div class="receipt-container">
<div class="receipt-header">
<div class="receipt-title">ROGMUKTI DIAGNOSTIC CENTRE</div>
<div style="font-size:13px; color:#475569; margin-top:4px;">Mollah stand, Auliapur, Patuakhali</div>
<div style="font-size:13px; color:#475569; font-weight: bold;">Mobile: 01711867637</div>
</div>
<table style="width:100%; font-size:14px; margin-bottom:10px; color:#1e293b; line-height: 1.4;">
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
<div style="font-weight:bold; color:#1e3a8a; border-bottom:1px solid #cbd5e1; padding-bottom:4px; font-size:14px;">Test Description & Rate</div>
<table class="receipt-table">
<thead>
<tr>
<th style="width:10%; text-align:center;">SL</th>
<th style="width:65%;">Test Name</th>
<th style="width:25%; text-align:right;">Price</th>
</tr>
</thead>
<tbody>"""

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
            t_name = test_item.split("(")[0].strip()
            t_price = test_item.split("(")[1].replace(")", "").strip()
            try:
                t_price_formatted = f"{float(t_price):.2f}"
            except:
                t_price_formatted = t_price
        else:
            t_name = test_item
            t_price_formatted = "0.00"
            
        receipt_html += f"""<tr>
<td style="text-align:center;">{serial_no}</td>
<td>{t_name}</td>
<td style="text-align:right;">{t_price_formatted} Tk</td>
</tr>"""
        serial_no += 1

    receipt_html += f"""</tbody>
</table>
<div style="margin-top:15px; border-top:1px dashed #cbd5e1; padding-top:8px; line-height: 1.4;">
<div class="summary-text"><b>Total Bill:</b> {total_bill:.2f} Tk</div>
<div class="summary-text"><b>Discount:</b> {discount_tk:.2f} Tk</div>
<div class="summary-text"><b>Advance Paid:</b> {advance_paid:.2f} Tk</div>
<div class="summary-text" style="font-size:15px; color:#ef4444; margin-top:4px;"><b>Due Amount:</b> {due_amount:.2f} Tk</div>
</div>
<div style="text-align:center; margin-top:25px; font-size:12px; color:#64748b; font-style:italic;">
Thank you for trusting us with your care.
</div>
</div>"""
    
    st.markdown(receipt_html, unsafe_allow_html=True)

else:
    if invoice_id > 0:
        st.error(f"🚨 দুঃখিত, #{invoice_id} নম্বরের কোনো বিল ডাটাবেজে খুঁজে পাওয়া যায়নি!")
    else:
        st.info("ℹ️ বিল প্রিন্ট করার জন্য উপরে সঠিক Invoice ID নম্বরটি ইনপুট দিন।")

conn.close()
