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
discount_pct = float(row[7])
advance_paid = float(row[8])
due_amount = float(row[9])
current_date = row[10]

# Calculate Discount Amount
discount_amount = (total_amount * discount_pct) / 100.0

# --- নতুন লজিক: কমা দিয়ে যুক্ত টেস্ট এবং ব্র্যাকেটের রেট আলাদা করা ---
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
        
    table_rows += f"<tr><td style='text-align: center;'>{index}</td><td>{t_name_clean}</td><td style='text-align: right;'>{t_price_val:.2f} Tk</td></tr>"
    index += 1

# ------------------- Full HTML, CSS and Print Logic -------------------
full_html_page = """
<style>
.receipt-box {
    max-width: 550px;
    margin: 20px auto;
    padding: 25px;
    border: 2px solid #1a365d;
    border-radius: 12px;
    background-color: white;
    color: black;
    font-family: 'Arial', sans-serif;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.header {
    text-align: center;
    background-color: #1a365d;
    color: white;
    padding: 15px;
    border-radius: 8px 8px 0 0;
    margin-bottom: 15px;
}
.header h2 { margin: 0; font-size: 24px; font-weight: bold; text-transform: uppercase; }
.header p { margin: 5px 0 0 0; font-size: 13px; opacity: 0.9; }
.info-table, .test-table { width: 100%; border-collapse: collapse; margin-bottom: 10px; color: black; }
.info-table td { padding: 5px 0; font-size: 14px; }
.test-table th, .test-table td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 13px; }
.test-table th { background-color: #f2f2f2; color: #1a365d; font-weight: bold; }
.total-section { text-align: right; font-size: 15px; line-height: 1.6; }
.total-section b { color: #1a365d; }

/* MONEY RECEIPT সেন্ট্রাল পয়েন্ট স্টাইল (রোগীর নামের উপরে) */
.money-receipt-title {
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    letter-spacing: 2px;
    margin: 10px 0 20px 0;
    color: #1a365d;
    text-transform: uppercase;
    border-bottom: 2px solid #1a365d;
    padding-bottom: 5px;
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
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        display: block !important;
    }
    @page {
        size: A4 portrait;
        margin: 15mm 10mm 10mm 10mm;
    }
}
</style>

<div class="receipt-box">
    <!-- Receipts Official Header Section -->
    <div class="header">
        <h2>Rogmukti Diagnostic Centre</h2>
        <p style="font-size: 15px; font-weight: bold; margin-top: 3px;">Mollah stand, Auliapur, Patuakhali</p>
        <p style="font-size: 13px;">📞 Mobile: 01711867637</p>
    </div>
    
    <!-- রোগীর নামের ঠিক উপরে MONEY RECEIPT টাইটেল -->
    <div class="money-receipt-title">MONEY RECEIPT</div>
    
    <!-- Patient Info Section in English -->
    <table class="info-table">
        <tr>
            <td><b>Invoice ID:</b> #__INVOICE_ID__</td>
            <td style="text-align: right;"><b>Date:</b> __CURRENT_DATE__</td>
        </tr>
        <tr>
            <td><b>Patient Name:</b> __NAME__</td>
            <td style="text-align: right;"><b>Age:</b> __AGE__ Y</td>
        </tr>
        <tr>
            <td><b>Mobile No:</b> __PHONE__</td>
            <td style="text-align: right;"><b>Ref. By:</b> __DOCTOR__</td>
        </tr>
    </table>
    
    <h3 style="color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 5px; font-size: 15px; margin-top: 15px;">Test Description & Rate</h3>
    <table class="test-table">
        <thead>
            <tr>
                <th style="width: 10%; text-align: center;">SL</th>
                <th style="width: 65%;">Test Name</th>
                <th style="width: 25%; text-align: right;">Price</th>
            </tr>
        </thead>
        <tbody>
            __TABLE_ROWS__
        </tbody>
    </table>
    
    <!-- Cost Breakdowns in English -->
    <div class="total-section">
        <p>Total Bill: __TOTAL_AMOUNT__ Tk</p>
        <p>Discount: __DISCOUNT_AMOUNT__ Tk (__DISCOUNT_PCT__%)</p>
        <p>Advance Paid: <b>__ADVANCE_PAID__ Tk</b></p>
        <p style="font-size: 16px; border-top: 1px dashed #1a365d; padding-top: 5px; margin-top: 5px;">
            <b>Due Amount: <span style="color: red;">__DUE_AMOUNT__ Tk</span></b>
        </p>
    </div>
    
    <div style="margin-top: 30px; text-align: center; font-size: 12px; color: #555; border-top: 1px solid #eee; padding-top: 10px;">
        <p>Thank you for trusting us with your care.</p>
    </div>
</div>
"""

# ডেটাবেজের মানগুলো নিরাপদে HTML টেমপ্লেটে রিপ্লেস করা হচ্ছে
full_html_page = full_html_page.replace("__INVOICE_ID__", str(invoice_id))
full_html_page = full_html_page.replace("__CURRENT_DATE__", str(current_date))
full_html_page = full_html_page.replace("__NAME__", str(name))
full_html_page = full_html_page.replace("__AGE__", str(age))
full_html_page = full_html_page.replace("__PHONE__", str(phone))
full_html_page = full_html_page.replace("__DOCTOR__", str(doctor))
full_html_page = full_html_page.replace("__TABLE_ROWS__", table_rows)
full_html_page = full_html_page.replace("__TOTAL_AMOUNT__", f"{total_amount:.2f}")
full_html_page = full_html_page.replace("__DISCOUNT_AMOUNT__", f"{discount_amount:.2f}")
full_html_page = full_html_page.replace("__DISCOUNT_PCT__", str(discount_pct))
full_html_page = full_html_page.replace("__ADVANCE_PAID__", f"{advance_paid:.2f}")
full_html_page = full_html_page.replace("__DUE_AMOUNT__", f"{due_amount:.2f}")

# ------------------- 1. Streamlit Print Button -------------------
if st.button("🖨️ Print Money Receipt Now", type="primary", use_container_width=True):
    st.components.v1.html("<script>parent.window.print();</script>", height=0)

# ------------------- 2. Render Main Content -------------------
st.html(full_html_page)
