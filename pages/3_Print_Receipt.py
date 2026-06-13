import streamlit as st
import sqlite3
import os
import re

# Security or login check
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first.")
    st.stop()

st.title("🏥 Medical Receipt Print")
st.write("------------------- Invoice ID Info -------------------")

invoice_id = None

# Read invoice ID from query parameters or session state
if "invoice_id" in st.query_params:
    invoice_id = st.query_params.get("invoice_id")
elif "last_invoice_id" in st.session_state:
    invoice_id = st.session_state.last_invoice_id

if not invoice_id:
    st.info("💡 No Invoice ID found. Please submit data from 'Patient Entry' page.")
    st.stop()

# Fix Directory Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rogmukti_clinic_fix.db")

# Database Connection
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("SELECT * FROM billing_records WHERE id = ?", (invoice_id,))
row = c.fetchone()
conn.close()

if not row:
    st.error(f"❌ No record found for ID #{invoice_id}.")
    st.stop()

# Assign variables from database row index
name = row[1]
age = row[2]
phone = row[3]
doctor = row[4]
selected_tests_data = row[5] 
total_amount = float(row[6])
discount_amount = float(row[7])
advance_paid = float(row[8])
due_amount = float(row[9])
current_date = row[10]

# --- কমা দিয়ে যুক্ত টেস্ট এবং ব্র্যাকেটের রেট আলাদা করা ---
tests_found = re.findall(r'([^,(\d]+)\s*(?:\(([\d.]+)\))?', selected_tests_data)

table_rows = ""
index = 1
for t_name, t_price in tests_found:
    t_name_clean = t_name.strip()
    if not t_name_clean:
        continue
        
    t_price_clean = t_price.strip() if t_price else "0.00"
    try:
        t_price_val = float(t_price_clean)
    except:
        t_price_val = 0.00
        
    table_rows += f"<tr><td style='text-align: center; border: 1px solid #333;'>{index}</td><td style='border: 1px solid #333; padding-left: 10px; font-weight: bold;'>{t_name_clean}</td><td style='text-align: right; border: 1px solid #333; padding-right: 10px; font-weight: bold;'>{t_price_val:.2f} Tk</td></tr>"
    index += 1

# ------------------- Full HTML, CSS and Print Logic -------------------
full_html_page = """
<style>
.receipt-box {
    max-width: 100%;
    margin: 10px auto;
    padding: 30px;
    border: 2px solid #000000 !important;
    background-color: white;
    color: black;
    font-family: 'Arial', sans-serif;
    box-sizing: border-box;
}
.header {
    text-align: center;
    border-bottom: 3px double #000000;
    padding-bottom: 12px;
    margin-bottom: 15px;
}
.header h2 { margin: 0; font-size: 28px; font-weight: bold; text-transform: uppercase; color: #000; }
.header p { margin: 4px 0 0 0; font-size: 15px; font-weight: 500; }

.money-receipt-title {
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 3px;
    margin: 15px auto;
    color: #000;
    border: 1.5px solid #000;
    width: 280px;
    padding: 6px 0;
    text-transform: uppercase;
    white-space: nowrap;
}

/* রোগীর তথ্যের টেবিল সিস্টেম স্টাইল */
.info-table { 
    width: 100%; 
    border-collapse: collapse; 
    margin-bottom: 25px; 
}
.info-table td { 
    padding: 8px 12px; 
    font-size: 14px; 
    color: #000;
    border: 1px solid #333; /* নিখুঁত ছক তৈরি করার বর্ডার */
}
.info-label {
    font-weight: bold;
    background-color: #f9fafb; /* লেবেলের জন্য হালকা ব্যাকগ্রাউন্ড */
}

.test-table { 
    width: 100%; 
    border-collapse: collapse; 
    margin-bottom: 20px; 
}
.test-table th { 
    border: 1px solid #333; 
    padding: 10px; 
    text-align: left; 
    font-size: 15px; 
    background-color: #f5f5f5; 
    color: #000; 
    font-weight: bold; 
}

.bill-footer-container {
    width: 100%;
    margin-top: 20px;
    display: block;
}

.total-section { 
    margin-left: auto;
    width: 300px;
    font-size: 15px; 
    line-height: 2.0; 
    border: 2px solid #1a365d;
    border-radius: 6px;
    padding: 12px 15px;
    background-color: #f8fafc !important;
}
.total-section table {
    width: 100%;
    border-collapse: collapse;
}
.total-section td {
    padding: 2px 0;
    color: #000;
}
.due-row {
    font-size: 17px; 
    font-weight: bold; 
    border-top: 1px dashed #1a365d;
    padding-top: 6px !important;
    margin-top: 4px;
}

.signature-section {
    margin-top: 50px;
    width: 100%;
    display: block;
}
.signature-wrapper {
    width: 200px;
    margin-left: auto;
    text-align: center;
}
.signature-line {
    border-top: 1.5px solid #000;
    font-size: 14px;
    font-weight: bold;
    padding-top: 5px;
    color: #000;
}

@media print {
    header, footer, [data-testid="stSidebar"], [data-testid="stHeader"], .stButton, h1, div.stWrite {
        display: none !important;
    }
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    .receipt-box {
        box-shadow: none !important;
        padding: 30px !important;
        margin: 0 auto !important;
        width: 100% !important;
        max-width: 100% !important;
        display: block !important;
        border: 2px solid #000000 !important;
    }
    .total-section {
        margin-left: auto !important;
        float: right !important;
        background-color: #f8fafc !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .signature-wrapper {
        margin-left: auto !important;
        float: right !important;
    }
    @page {
        size: A4 portrait;
        margin: 8mm 10mm 10mm 10mm;
    }
}
</style>

<div class="receipt-box">
    <div class="header">
        <h2>Rogmukti Diagnostic Centre</h2>
        <p>Mollah stand, Auliapur, Patuakhali</p>
        <p>📞 Mobile: 01711867637</p>
    </div>
    
    <div class="money-receipt-title">MONEY RECEIPT</div>
    
    <!-- নতুন টেবিল সিস্টেম আকারে সাজানো রোগীর তথ্য -->
    <table class="info-table">
        <tr>
            <td class="info-label" style="width: 20%;">Invoice ID:</td>
            <td style="width: 30%;">#__INVOICE_ID__</td>
            <td class="info-label" style="width: 20%;">Date:</td>
            <td style="width: 30%;">__CURRENT_DATE__</td>
        </tr>
        <tr>
            <td class="info-label">Patient Name:</td>
            <td>__NAME__</td>
            <td class="info-label">Age / Sex:</td>
            <td>__AGE__ Y</td>
        </tr>
        <tr>
            <td class="info-label">Ref. By:</td>
            <td>__DOCTOR__</td>
            <td class="info-label">Mobile No:</td>
            <td>__PHONE__</td>
        </tr>
    </table>
    
    <table class="test-table">
        <thead>
            <tr>
                <th style="width: 10%; text-align: center;">SL</th>
                <th style="width: 65%; padding-left: 10px;">Test Name</th>
                <th style="width: 25%; text-align: right; padding-right: 10px;">Price</th>
            </tr>
        </thead>
        <tbody>
            __TABLE_ROWS__
        </tbody>
    </table>
    
    <div class="bill-footer-container">
        <div class="total-section">
            <table>
                <tr>
                    <td style="font-weight: 600;">Total Bill</td>
                    <td style="text-align: right; font-weight: 600;">__TOTAL_AMOUNT__ Tk</td>
                </tr>
                <tr>
                    <td style="color: #475569;">Discount</td>
                    <td style="text-align: right; color: #475569;">__DISCOUNT_AMOUNT__ Tk</td>
                </tr>
                <tr>
                    <td style="color: #475569; padding-bottom: 6px;">Advance Paid</td>
                    <td style="text-align: right; color: #475569; padding-bottom: 6px;">__ADVANCE_PAID__ Tk</td>
                </tr>
                <tr class="due-row">
                    <td style="padding-top: 6px;">Due Amount</td>
                    <td style="text-align: right; color: #dc2626; padding-top: 6px;">__DUE_AMOUNT__ Tk</td>
                </tr>
            </table>
        </div>
    </div>
    
    <div class="signature-section">
        <div class="signature-wrapper">
            <div class="signature-line">Authorized Signature</div>
        </div>
    </div>
    
    <div style="margin-top: 35px; text-align: center; font-size: 12px; color: #555; border-top: 1px solid #ddd; padding-top: 10px; clear: both;">
        <p>Thank you for trusting us with your care.</p>
    </div>
</div>
"""

# রিপ্লেস লজিক
full_html_page = full_html_page.replace("__INVOICE_ID__", str(invoice_id))
full_html_page = full_html_page.replace("__CURRENT_DATE__", str(current_date))
full_html_page = full_html_page.replace("__NAME__", str(name))
full_html_page = full_html_page.replace("__AGE__", str(age))
full_html_page = full_html_page.replace("__PHONE__", str(phone))
full_html_page = full_html_page.replace("__DOCTOR__", str(doctor))
full_html_page = full_html_page.replace("__TABLE_ROWS__", table_rows)
full_html_page = full_html_page.replace("__TOTAL_AMOUNT__", f"{total_amount:.2f}")
full_html_page = full_html_page.replace("__DISCOUNT_AMOUNT__", f"{discount_amount:.2f}")
full_html_page = full_html_page.replace("__ADVANCE_PAID__", f"{advance_paid:.2f}")
full_html_page = full_html_page.replace("__DUE_AMOUNT__", f"{due_amount:.2f}")

# ------------------- 1. Streamlit Print Button -------------------
if st.button("🖨️ Print Money Receipt Now", type="primary", use_container_width=True):
    st.components.v1.html("<script>parent.window.print();</script>", height=0)

# ------------------- 2. Render Main Content -------------------
st.html(full_html_page)
