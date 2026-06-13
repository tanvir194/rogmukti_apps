import sys
import os
import streamlit as st
import sqlite3

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Money Receipt", layout="wide")

# ২. কাস্টম ডার্ক মোড এবং রিসিটের ফুল-উইডথ ও ফ্রেম CSS
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
    
    /* 📄 স্ক্রিন ভিউ ডিজাইন (সফটওয়্যারে দেখার জন্য) */
    .receipt-container {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 12px;
        padding: 30px;
        max-width: 100% !important; /* স্ক্রিনেও চওড়া দেখাবে */
        margin: 0 auto;
        font-family: 'Segoe UI', Arial, sans-serif;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        border: 2px solid #000000;
    }
    .receipt-header {
        text-align: center;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }
    .receipt-title {
        color: #1e3a8a !important;
        font-size: 28px;
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
        padding: 12px 10px;
        text-align: left;
    }
    .receipt-table td {
        border-bottom: 1px solid #e2e8f0 !important;
        padding: 12px 10px;
        color: #334155 !important;
    }
    .summary-text {
        text-align: right;
        font-size: 16px;
        margin-top: 6px;
        color: #1e293b !important;
    }
    
    /* 🖨️ প্রিন্ট স্ক্রিপ্ট (A4 ফুল স্ক্রিন চওড়া ও ফ্রেম আবদ্ধ করার আসল লজিক) */
    @media print {
        body * {
            visibility: hidden !important;
        }
        .receipt-container, .receipt-container * {
            visibility: visible !important;
        }
        
        .receipt-container {
            position: absolute !important;
            left: -50 !important; 
            top: -50 !important;
            width: -125% !important;  
            max-width: 100% !important;
            box-shadow: none !important;
            border: 3px solid #000000 !important; /* চারদিকের ফ্রেম বা বর্ডার */
            padding: 30px !important;  
            margin: -10px !important;
            line-height: 2.5 !important;
            display: block !important;
            height: auto !important; 
            box-sizing: border-box !important;
        }
        
        .receipt-header {
            margin-bottom: 30px !important;
            padding-bottom: 152px !important;
            border-bottom: 3px solid #1e3a8a !important;
        }
        
        .receipt-table th {
            padding: 10px !important;
            font-size: 15px !important;
            background-color: #f1f5f9 !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            border-bottom: 2px solid #000000 !important;
        }
        .receipt-table td {
            padding: 10px !important; 
            font-size: 25px !important;
            border-bottom: 1px solid #cbd5e1 !important;
        }
        .summary-text {
            margin-top: 8px !important;
            font-size: 20px !important;
        }
        
        @page {
            size: A4;
            margin: 5mm !important; 
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🖨️ Full Width A4 English Money Receipt")

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

    # HTML রিসিট জেনারেট করা
    receipt_html = f"""<div class="receipt-container">
<div class="receipt-header">
<div class="receipt-title">ROGMUKTI DIAGNOSTIC CENTRE</div>
<div style="font-size:14px; color:#475569; margin-top:6px;">Mollah stand, Auliapur, Patuakhali</div>
<div style="font-size:14px; color:#1e3a8a; font-weight: bold; margin-top:4px;">Mobile: 01711867637</div>
</div>
<table style="width:100%; font-size:15px; margin-bottom:25px; color:#1e293b; line-height: 1.6;">
<tr>
<td style="width:50%;"><b>Invoice ID:</b> #{p_id}</td>
<td style="text-align:right; width:50%;"><b>Date:</b> {billing_date}</td>
</tr>
<tr>
<td><b>Patient Name:</b> {p_name}</td>
<td style="text-align:right; width:50%;"><b>Age:</b> {p_age} Y</td>
</tr>
<tr>
<td><b>Mobile No:</b> {p_phone}</td>
<td style="text-align:right; width:50%;"><b>Ref. By:</b> {p_doctor}</td>
</tr>
</table>
<div style="font-weight:bold; color:#1e3a8a; border-bottom:1px solid #cbd5e1; padding-bottom:6px; font-size:16px;">Test Description & Rate</div>
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
            # 🛠️ ফিক্সড: পাইথন লিস্ট ইনডেক্সিং এর ভুলটি এখানে পুরোপুরি সমাধান করা হয়েছে
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
            
        receipt_html += f"""<tr>
<td style="text-align:center;">{serial_no}</td>
<td>{t_name}</td>
<td style="text-align:right;">{t_price_formatted} Tk</td>
</tr>"""
        serial_no += 1

    try:
        t_bill = float(total_bill)
        d_tk = float(discount_tk)
        a_paid = float(advance_paid)
        d_amt = float(due_amount)
    except:
        t_bill, d_tk, a_paid, d_amt = 0.0, 0.0, 0.0, 0.0

    receipt_html += f"""</tbody>
</table>
<div style="margin-top:25px; border-top:1px dashed #cbd5e1; padding-top:12px;">
<div class="summary-text"><b>Total Bill:</b> {t_bill:.2f} Tk</div>
<div class="summary-text"><b>Discount:</b> {d_tk:.2f} Tk</div>
<div class="summary-text"><b>Advance Paid:</b> {a_paid:.2f} Tk</div>
<div class="summary-text" style="font-size:18px; color:#ef4444; margin-top:6px;"><b>Due Amount:</b> {d_amt:.2f} Tk</div>
</div>
<div style="text-align:center; margin-top:50px; font-size:14px; color:#64748b; font-style:italic;">
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
