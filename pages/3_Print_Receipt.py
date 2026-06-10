import streamlit as st
import sqlite3

# লগইন চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ আগে লগইন করুন")
    st.stop()

st.title("🖨️ মেডিকেল রিসিপ্ট প্রিন্ট")
# ================== Invoice ID নেওয়া ==================
invoice_id = None

if "invoice_id" in st.query_params:
    invoice_id = st.query_params.get("invoice_id")
elif "last_invoice_id" in st.session_state:
    invoice_id = st.session_state.last_invoice_id

if not invoice_id:
    st.info("কোনো বিল সিলেক্ট করা হয়নি। 'Patient Entry' পেজ থেকে বিল সেভ করে আসুন।")
    st.stop()
    # ================== ডাটাবেস থেকে ডাটা নেওয়া ==================
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()
c.execute("SELECT * FROM billing_records WHERE id = ?", (invoice_id,))
row = c.fetchone()
conn.close()

if not row:
    st.error(f"ID #{invoice_id} এর বিল পাওয়া যায়নি")
    st.stop()

# ডাটা ভ্যারিয়েবলে রাখা
name = row[1]
age = row[3]
phone = row[2]
doctor = row[4]
selected_tests_data = row[5]
total_amount = float(row[6])
discount_pct = float(row[7])
advance_paid = float(row[8])
due_amount = float(row[9])
current_date = row[10]

discount_amount = (total_amount * discount_pct) / 100.0
due_amount = total_amount - discount_amount - advance_paid

tests_list = [item.strip() for item in selected_tests_data.split("|") if item.strip()]
# ================== প্রিন্ট বাটন ==================
st.components.v1.html("""
    <button onclick="parent.window.print()" style="background:#1a365d;color:white;padding:14px 30px;
    border:none;border-radius:8px;cursor:pointer;font-size:18px;font-weight:bold;width:100%;height:65px;">
    🖨️ রিসিপ্ট প্রিন্ট করুন (Print Now)
    </button>
""", height=80)

# ================== CSS ==================
st.markdown("""
<style>
@media print {
    body * { visibility: hidden; }
    #receipt, #receipt * { visibility: visible; }
    #receipt { position: absolute; left: 0; top: 0; width: 100%; }
    @page { size: A4 portrait; margin: 10mm; }
}
.receipt {
    max-width: 800px;
    margin: 20px auto;
    padding: 30px;
    border: 3px solid #1a365d;
    border-radius: 12px;
    background: white;
    font-family: Arial, sans-serif;
    color: black;
}
.header {
    text-align: center;
    background: #1a365d;
    color: white;
    padding: 25px;
    border-radius: 8px 8px 0 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}
th, td {
    border: 1px solid #ccc;
    padding: 10px;
}
th { background: #3182ce; color: white; }
.summary {
    text-align: right;
    font-size: 18px;
    margin-top: 25px;
    line-height: 1.9;
}
</style>
""", unsafe_allow_html=True)
# ================== টেস্টের টেবিল রো তৈরি ==================
table_rows = ""
for item in tests_list:
    if ":" in item:
        parts = item.split(":", 1)
        t_name = parts[0].strip()
        try:
            t_price = float(parts[1].strip())
        except:
            t_price = 0.0
    else:
        t_name = item
        t_price = 0.0
    
    table_rows += f"<tr><td>{t_name}</td><td style='text-align:right;'>{t_price:.2f}</td></tr>"

# ================== মূল রিসিপ্ট HTML ==================
receipt_html = f"""
<div id="receipt" class="receipt">
    <div class="header">
        <h1 style="margin:0; font-size:32px;">ROG MUKTI</h1>
        <p style="margin:8px 0 0 0; font-size:16px;">Mollah Stand, Auliapur, Patuakhali</p>
    </div>

    <table>
        <tr><td><b>Bill No:</b> #{invoice_id}</td><td style="text-align:right;"><b>Date:</b> {current_date}</td></tr>
        <tr><td><b>Patient Name:</b> {name}</td><td style="text-align:right;"><b>Age:</b> {age} Years</td></tr>
        <tr><td><b>Phone Number:</b> {phone}</td><td style="text-align:right;"><b>Refd By:</b> {doctor}</td></tr>
    </table>

    <table>
        <thead><tr><th>Description (Test Name)</th><th style="text-align:right;">Amount</th></tr></thead>
        <tbody>{table_rows}</tbody>
    </table>

    <div class="summary">
        <p><b>Total Amount:</b> {total_amount:.2f} ৳</p>
        <p><b>Discount ({discount_pct}%):</b> -{discount_amount:.2f} ৳</p>
        <p><b>Advance Paid:</b> -{advance_paid:.2f} ৳</p>
        <p style="color:red; font-size:24px; border-top:3px solid #1a365d; padding-top:12px;">
            <b>Due Amount: {due_amount:.2f} ৳</b>
        </p>
    </div>
</div>
"""

st.markdown(receipt_html, unsafe_allow_html=True)
