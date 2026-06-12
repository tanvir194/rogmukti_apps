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
    .stButton button, .stDownloadButton button {
        background-color: #0284c7 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        width: 100%;
        font-size: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* 📄 রিসিট প্রিভিউ ডিজাইন */
    .receipt-container {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border-radius: 16px;
        padding: 40px;
        max-width: 720px;
        margin: 0 auto;
        font-family: 'Segoe UI', system-ui, sans-serif;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        border: 1px solid #e2e8f0;
    }
    .receipt-header {
        text-align: center;
        border-bottom: 3px double #1e3a8a;
        padding-bottom: 18px;
        margin-bottom: 25px;
    }
    .receipt-title {
        color: #1e3a8a !important;
        font-size: 30px;
        font-weight: 800;
        margin: 0;
        letter-spacing: 1px;
    }
    .receipt-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }
    .receipt-table th {
        background-color: #f1f5f9;
        color: #1e3a8a;
        border-top: 1px solid #cbd5e1;
        border-bottom: 2px solid #1e3a8a;
        padding: 12px 10px;
        text-align: left;
        font-weight: 700;
        font-size: 14px;
        text-transform: uppercase;
    }
    .receipt-table td {
        border-bottom: 1px solid #f1f5f9;
        padding: 12px 10px;
        color: #334155;
        font-size: 15px;
    }
    .summary-box {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 15px;
        margin-top: 25px;
        border: 1px solid #e2e8f0;
        width: 50%;
        margin-left: auto;
    }
    .summary-text {
        display: flex;
        justify-content: space-between;
        font-size: 14px;
        margin-top: 6px;
        color: #334155;
    }
    
    /* 🖨️ A4 পেপার প্রিন্টিং ফিক্স */
    @media print {
        header, [data-testid="stSidebar"], .stButton, .stNumberInput, div.block-container button, .stDownloadButton {
            display: none !important;
            visibility: hidden !important;
        }
        body {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .stApp {
            background-color: #ffffff !important;
        }
        .receipt-container {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            max-width: 100%;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
        }
        @page {
            size: A4;
            margin: 20mm;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🖨️ Premium English Money Receipt")

# ডাটাবেজ থেকে ডাটা কুয়েরি করা
record = None
invoice_id = 0

try:
    conn = sqlite3.connect("rogmukti_clinic_fix.db")
    c = conn.cursor()

    default_invoice = st.session_state.get('last_invoice_id', 0)

    col_search1, col_search2 = st.columns(2)
    with col_search1:
        invoice_id = st.number_input("Enter Bill No / Invoice ID to Print:", min_value=0, value=int(default_invoice), step=1)

    c.execute("SELECT * FROM billing_records WHERE id=?", (invoice_id,))
    record = c.fetchone()
    conn.close()
except Exception as e:
    st.error(f"Database Error: {e}")

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

    # ফাইল ডাউনলোডের কাস্টম এমবেডেড প্রিমিয়াম CSS স্টাইল
    embedded_css = """
    <style>
    .receipt-container { background-color: #ffffff !important; color: #1e293b !important; border-radius: 16px; padding: 40px; max-width: 680px; margin: 25px auto; font-family: 'Segoe UI', system-ui, sans-serif; border: 1px solid #e2e8f0; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
    .receipt-header { text-align: center; border-bottom: 3px double #1e3a8a; padding-bottom: 18px; margin-bottom: 25px; }
    .receipt-title { color: #1e3a8a !important; font-size: 28px; font-weight: bold; margin: 0; letter-spacing: 0.5px; }
    .receipt-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    .receipt-table th { background-color: #f1f5f9; color: #1e3a8a; border-top: 1px solid #cbd5e1; border-bottom: 2px solid #1e3a8a; padding: 12px 10px; text-align: left; font-weight: 700; font-size: 14px; text-transform: uppercase; }
    .receipt-table td { border-bottom: 1px solid #f1f5f9; padding: 12px 10px; color: #334155; font-size: 15px; }
    .summary-box { background-color: #f8fafc; border-radius: 8px; padding: 15px; margin-top: 25px; border: 1px solid #e2e8f0; width: 55%; margin-left: auto; }
    .summary-text { display: table; width: 100%; font-size: 14px; margin-top: 6px; color: #334155; }
    .summary-left { display: table-cell; text-align: left; font-weight: bold; }
    .summary-right { display: table-cell; text-align: right; }
    </style>
    """

    # HTML রিসিট জেনারেট করা
    receipt_html = f"""<div class="receipt-container">
<div class="receipt-header">
<div class="receipt-title">ROGMUKTI DIAGNOSTIC CENTRE</div>
<div style="font-size:14px; color:#475569; margin-top:6px;">Mollah stand, Auliapur, Patuakhali</div>
<div style="font-size:14px; color:#1e3a8a; font-weight: bold; margin-top:4px;">Mobile: 01711867637</div>
</div>
<table style="width:100%; font-size:15px; margin-bottom:25px; color:#334155; line-height: 1.7; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px;">
<tr>
<td style="width:50%;"><b>Invoice ID:</b> <span style="color:#0284c7; font-weight:700;">#{p_id}</span></td>
<td style="text-align:right; width:50%;"><b>Date:</b> {billing_date}</td>
</tr>
<tr>
<td><b>Patient Name:</b> {p_name}</td>
<td style="text-align:right; width:50%;"><b>Age / Sex:</b> {p_age} Y</td>
</tr>
<tr>
<td><b>Mobile No:</b> {p_phone}</td>
<td style="text-align:right; width:50%;"><b>Ref. By:</b> <span style="color:#1e3a8a; font-weight:600;">{p_doctor}</span></td>
</tr>
</table>
<div style="font-weight:bold; color:#1e3a8a; font-size:16px; letter-spacing: 0.3px;">Test Description & Rate</div>
<table class="receipt-table">
<thead>
<tr>
<th style="width:12%; text-align:center;">SL</th>
<th style="width:63%;">Test Name</th>
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
            # 🛠️ টেক্সট স্প্লিটিং মেথড এবার ১০০% নির্ভুলভাবে লেখা হয়েছে
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
<td style="text-align:center; color:#64748b;">{serial_no}</td>
<td style="font-weight:500;">{t_name}</td>
<td style="text-align:right; font-weight:600;">{t_price_formatted} Tk</td>
</tr>"""
        serial_no += 1

    try:
        total_bill_val = float(total_bill)
        discount_tk_val = float(discount_tk)
        advance_paid_val = float(advance_paid)
        due_amount_val = float(due_amount)
    except:
        total_bill_val, discount_tk_val, advance_paid_val, due_amount_val = 0.0, 0.0, 0.0, 0.0

    receipt_html += f"""</tbody>
</table>
<div class="summary-box">
<div class="summary-text"><span class="summary-left" style="font-weight:500;">Total Bill:</span><span class="summary-right">{total_bill_val:.2f} Tk</span></div>
<div class="summary-text"><span class="summary-left" style="font-weight:500;">Discount:</span><span class="summary-right" style="color:#16a34a;">- {discount_tk_val:.2f} Tk</span></div>
<div class="summary-text"><span class="summary-left" style="font-weight:500;">Advance Paid:</span><span class="summary-right" style="color:#2563eb;">{advance_paid_val:.2f} Tk</span></div>
<div class="summary-text" style="border-top: 1px solid #cbd5e1; margin-top: 8px; padding-top: 8px; font-size:16px;"><span class="summary-left" style="color:#ef4444; font-weight:700;">Due Amount:</span><span class="summary-right" style="color:#ef4444; font-weight:700;">{due_amount_val:.2f} Tk</span></div>
</div>
<div style="text-align:center; margin-top:50px; font-size:13px; color:#94a3b8; font-style:italic; border-top: 1px dashed #e2e8f0; padding-top: 15px;">
Thank you for trusting us with your care.
</div>
</div>"""

    downloadable_html = embedded_css + receipt_html

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🖨️ Print Receipt (For PC)"):
