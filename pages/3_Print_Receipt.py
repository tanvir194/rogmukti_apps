import streamlit as st
import sqlite3
import os
import importlib.util
import os

# মেসেজ পাঠানোর ফাইলটি লোড করার সঠিক নিয়ম
sms_path = os.path.join(os.path.dirname(__path__[0] if '__path__' in locals() else os.path.abspath(__file__)), "10_Send_SMS.py")
spec = importlib.util.spec_from_file_location("Send_SMS", sms_path)
sms_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sms_module)

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
    # মেসেজটি ইতিমধ্যে পাঠানো হয়েছে কিনা তা চেক করা হচ্ছে
    if f"sms_sent_{invoice_id}" not in st.session_state:
        try:
            # রুগীর মোবাইলে মেসেজ পাঠানো হচ্ছে
            sms_module.send_patient_sms(patient_phone=phone, patient_name=name, invoice_amount=total_amount)
            # সেশন স্টেটে সংরক্ষণ করা হচ্ছে যাতে পেজ রিফ্রেশ হলে দ্বিতীয়বার মেসেজ না যায়
            st.session_state[f"sms_sent_{invoice_id}"] = True
        except Exception as e:
            st.error(f"SMS পাঠাতে ব্যর্থ: {e}")
            
# Calculate Discount Amount
discount_amount = (total_amount * discount_pct) / 100.0

# Split selected tests by pipe '|' symbol
tests_list = [item.strip() for item in selected_tests_data.split('|') if item.strip()]

# Create Dynamic HTML Table Rows for Tests
table_rows = ""
for index, item in enumerate(tests_list, start=1):
    if ":" in item:
        t_name, t_price = item.split(":", 1)
    else:
        t_name, t_price = item, "0.0"
    
    try:
        t_price_val = float(t_price)
    except:
        t_price_val = 0.0
        
    table_rows += f"<tr><td style='text-align: center;'>{index}</td><td>{t_name}</td><td style='text-align: right;'>{t_price_val:.2f} Tk</td></tr>"

# ------------------- Full HTML, CSS and Print Logic -------------------
full_html_page = f"""
<style>
.receipt-box {{
    max-width: 550px;
    margin: 20px auto;
    padding: 25px;
    border: 2px solid #1a365d;
    border-radius: 12px;
    background-color: white;
    color: black;
    font-family: 'Arial', sans-serif;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}}
.header {{
    text-align: center;
    background-color: #1a365d;
    color: white;
    padding: 15px;
    border-radius: 8px 8px 0 0;
    margin-bottom: 20px;
}}
.header h2 {{ margin: 0; font-size: 24px; font-weight: bold; text-transform: uppercase; }}
.header p {{ margin: 5px 0 0 0; font-size: 13px; opacity: 0.9; }}
.info-table, .test-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; color: black; }}
.info-table td {{ padding: 5px 0; font-size: 14px; }}
.test-table th, .test-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 13px; }}
.test-table th {{ background-color: #f2f2f2; color: #1a365d; font-weight: bold; }}
.total-section {{ text-align: right; font-size: 15px; line-height: 1.6; }}
.total-section b {{ color: #1a365d; }}

@media print {{
    header, footer, [data-testid="stSidebar"], [data-testid="stHeader"], .stButton, h1, div.stWrite {{
        display: none !important;
    }}
    .main .block-container {{
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }}
    .receipt-box {{
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        display: block !important;
    }}
    @page {{
        size: A4 portrait;
        margin: 15mm 10mm 10mm 10mm;
    }}
}}
</style>

<div class="receipt-box">
    <!-- Receipts Official Header Section -->
    <div class="header">
        <h2>Rogmukti Diagnostic Centre</h2>
        <p style="font-size: 15px; font-weight: bold; margin-top: 3px;">Mollah stand, Auliapur, Patuakhali</p>
        <p style="font-size: 13px;">📞 Mobile: 01711867637</p>
    </div>
    
    <!-- Patient Info Section in English -->
    <table class="info-table">
        <tr>
            <td><b>Invoice ID:</b> #{invoice_id}</td>
            <td style="text-align: right;"><b>Date:</b> {current_date}</td>
        </tr>
        <tr>
            <td><b>Patient Name:</b> {name}</td>
            <td style="text-align: right;"><b>Age:</b> {age} Y</td>
        </tr>
        <tr>
            <td><b>Mobile No:</b> {phone}</td>
            <td style="text-align: right;"><b>Ref. By:</b> {doctor}</td>
        </tr>
    </table>
    
    <h3 style="color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 5px; font-size: 15px; margin-top: 10px;">Test Description & Rate</h3>
    <table class="test-table">
        <thead>
            <tr>
                <th style="width: 10%; text-align: center;">SL</th>
                <th style="width: 65%;">Test Name</th>
                <th style="width: 25%; text-align: right;">Price</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    
    <!-- Cost Breakdowns in English -->
    <div class="total-section">
        <p>Total Bill: {total_amount:.2f} Tk</p>
        <p>Discount: {discount_amount:.2f} Tk ({discount_pct}%)</p>
        <p>Advance Paid: <b>{advance_paid:.2f} Tk</b></p>
        <p style="font-size: 16px; border-top: 1px dashed #1a365d; padding-top: 5px; margin-top: 5px;">
            <b>Due Amount: <span style="color: red;">{due_amount:.2f} Tk</span></b>
        </p>
    </div>
    
    <div style="margin-top: 30px; text-align: center; font-size: 12px; color: #555; border-top: 1px solid #eee; padding-top: 10px;">
        <p>Thank you for trusting us with your care.</p>
    </div>
</div>
"""

# ------------------- 1. Streamlit Print Button -------------------
if st.button("🖨️ Print Money Receipt Now", type="primary", use_container_width=True):
    st.components.v1.html("<script>parent.window.print();</script>", height=0)

# ------------------- 2. Render Main Content -------------------
st.html(full_html_page)
