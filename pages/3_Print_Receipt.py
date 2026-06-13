import sys
import os
import streamlit as st
import sqlite3

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Money Receipt", layout="wide")

# ২. কাস্টম ডার্ক মোড এবং রিসিটের প্রিমিয়াম হোয়াইট কার্ড CSS
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
    
    /* 📄 রিসিট প্রিভিউ ডিজাইন (স্ক্রিনে যেমন দেখাবে) */
    .receipt-container {
        background-color: #ffffff !important;
        color: #000100 !important;
        border-radius: 12px;
        padding: 30px;
        max-width: 650px;
        margin: 0 auto;
        font-family: 'Segoe UI', Arial, sans-serif;
        box: 0 4px 15px rgba(5,5,5,5.5);
        border: 1px solid #cbd5e1;
    }
    .receipt-header {
        text-align: center;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 12px;
        margin-bottom: 20px;
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
        margin-top: 05px;
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
    
    /* 🖨️ প্রিন্ট করার সময় এই ডিজাইনটি চালু হবে (A4 Premium Fix) */
    @media print {
        header, [data-testid="stSidebar"], .stButton, .stNumberInput, div.block-container button {
            display: none !important;
            visibility: hidden !important;
        }
        body, .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .receipt-container {
            position: absolute !important;
            left: 5% !important;
            top: 0 !important;
            width: 80% !important;
            max-width: 100% !important;
            box-shadow: none !important;
            padding: 20px !important;
            margin: 0 !important;
            border: 1px solid #000000 !important;
            background: #ffffff !important;
            color: #000000 !important;
        }
        .receipt-table th {
            background-color: #f1f5f9 !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
            border-bottom: 2px solid #000000 !important;
        }
        .receipt-table td {
            border-bottom: 1px solid #cbd5e1 !important;
        }
        @page {
            size: A4;
            margin: 15mm;
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
    # 🛠️ বাটন ট্রিগার জাভাস্ক্রিপ্ট ফিক্স
    if st.button("🖨️ Print Money Receipt Now"):
        st.markdown("""
            <script>
                window.print();
            </script>
        """, unsafe_allow_html=True)
    st.write("")

# --- HTML স্ট্রিং রেন্ডারিং (Zero Indentation বজায় রাখা হয়েছে) ---
    receipt_html = f"""<div class="receipt-container">
<div class="receipt-header">
<div class="receipt-title">ROGMUKTI DIAGNOSTIC CENTRE</div>
<div style="font-size:13px; color:#475569; margin-top:4px;">Mollah stand, Auliapur, Patuakhali</div>
<div style="font-size:13px; color:#475569; font-weight: bold;">Mobile: 01711867637</div>
</div>
<table style="width:100%; font-size:14px; margin-bottom:15px; color:#1e293b;">
<tr>
<td><b>Invoice ID:</b> #{p_id}</td>
<td style="text-align:right;"><b>Date:</b> {billing_date}</td>
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
<div style="font-weight:bold; color:#1e3a8a; border-bottom:1px solid #cbd5e1; padding-bottom:4px; font-size:15px;">Test Description & Rate</div>
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
<div style="margin-top:20px; border-top:1px dashed #cbd5e1; padding-top:10px;">
<div class="summary-text"><b>Total Bill:</b> {total_bill:.2f} Tk</div>
<div class="summary-text"><b>Discount:</b> {discount_tk:.2f} Tk</div>
<div class="summary-text"><b>Advance Paid:</b> {advance_paid:.2f} Tk</div>
<div class="summary-text" style="font-size:16px; color:#ef4444; margin-top:6px;"><b>Due Amount:</b> {due_amount:.2f} Tk</div>
</div>
<div style="text-align:center; margin-top:35px; font-size:13px; color:#64748b; font-style:italic;">
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
