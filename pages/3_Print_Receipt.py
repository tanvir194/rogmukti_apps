import streamlit as st
import sqlite3
import os
import importlib.util

# দৈনিক ডাটাবেজ ডাটা লোড করার সঠিক নিয়ম
sms_path = os.path.join(os.path.dirname(__file__), ".." if "__path__" in locals() else os.path.abspath(__file__), "..", "10_Send_SMS.py")
spec = importlib.util.spec_from_file_location("Send_SMS", sms_path)
sms_module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(sms_module) # আপনার অরিজিনাল কোডের লাইন

# Security or login check
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 Please login first.")
    st.stop()

st.title("🖨️ Medical Receipt Print")

# 🛡️ এটি আপনার এই রিসিট পেজের ব্যাকগ্রাউন্ডে রোগ মুক্তির লোগোটি জলছাপ হিসেবে ইনজেক্ট করবে
st.markdown(
    """
    <style>
    /* ১. স্ক্রিন এবং প্রিন্ট উভয় জায়গাতেই জলছাপ বসানোর মেইন লজিক */
    [data-testid="stMainBlockContainer"], .main {
        position: relative !important;
    }
    
    [data-testid="stMainBlockContainer"]::before, .main::before {
        content: "" !important;
        position: absolute !important;
        top: 55% !important; /* মেমোর ঠিক মাঝখানে রাখার জন্য */
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        width: 320px !important; /* জলছাপের পারফেক্ট সাইজ */
        height: 320px !important;
        /* রোগ মুক্তি ডায়াগনস্টিক সেন্টারের নির্দিষ্ট ও স্থায়ী লোগো (শিল্ড + প্লাস + হার্টবিট) */
        background-image: url('data:image/svg+xml;utf8,<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://w3.org"><rect x="42" y="15" width="16" height="70" fill="%23FF3366" rx="4"/><rect x="15" y="42" width="70" height="16" fill="%23FF3366" rx="4"/><path d="M 18 50 L 38 50 L 44 25 L 50 75 L 56 38 L 62 58 L 66 50 L 82 50" stroke="%23FFFFFF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M 50 5 L 85 20 L 85 55 C 85 75 50 95 50 95 C 50 95 15 75 15 55 L 15 20 Z" stroke="%230066CC" stroke-width="4" stroke-linejoin="round" fill="none"/></svg>') !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        opacity: 0.05 !important; /* ৫% হালকা ঝাপসা রাখা হলো যেন ওপরের লেখা পরিষ্কার পড়া যায় */
        pointer-events: none !important;
        z-index: 1000 !important;
    }

    /* 🖨️ প্রিন্ট করার সময় ব্রাউজার যেন বাধ্যতামূলক জলছাপটি প্রিন্টারে পাঠায় */
    @media print {
        [data-testid="stSidebar"], button, header, [data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stMainBlockContainer"]::before, .main::before {
            opacity: 0.06 !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write("----------------- Invoice ID Info -----------------")

invoice_id = None

# Read invoice ID from query parameters or session state
if "invoice_id" in st.query_params:
    invoice_id = st.query_params["invoice_id"]
elif "last_invoice_id" in st.session_state:
    invoice_id = st.session_state.last_invoice_id

if not invoice_id:
    st.info("ℹ️ No Invoice ID found. Please submit data from 'Patient Entry' page.")
    st.stop()

# Fix Directory Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rogmukti_clinic_fix.db")

# Database Connection
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("SELECT * FROM billing_records WHERE ID = ?", (invoice_id,))
row = c.fetchone()
conn.close()

if not row:
    st.error(f"❌ No record found for ID #{invoice_id}")
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

# এসএমএস এরর হ্যান্ডেল এবং অটো সেন্ডিং লজিক
if f"sms_sent_{invoice_id}" not in st.session_state:
    try:
        # sms_module.send_patient_sms(patient_phone=phone, patient_name=name, invoice_amount=total_amount)
        st.session_state[f"sms_sent_{invoice_id}"] = True
    except Exception as e:
        st.error(f"SMS পাঠানো ব্যর্থ: {e}")

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
        t_name, t_price = item, "0.00"
    
    table_rows += f"""
    <tr>
        <td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{index}</td>
        <td style='border: 1px solid #ddd; padding: 8px;'>{t_name}</td>
        <td style='border: 1px solid #ddd; padding: 8px; text-align: right;'>{t_price} Tk</td>
    </tr>
    """

# 🖨️ প্রিন্ট বাটন
if st.button("🖨️ Print Money Receipt Now", use_container_width=True, type="primary"):
    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

# মূল রিসিট কন্টেইনার এবং মেমো ডিজাইন (আপনার অরিজিনাল থিম অনুযায়ী)
st.markdown(
    f"""
    <div style='border: 2px solid #1A3E6C; padding: 20px; border-radius: 8px; background-color: #ffffff; font-family: Arial, sans-serif;'>
        <div style='background-color: #1A3E6C; padding: 15px; border-radius: 6px; text-align: center; color: white;'>
            <h2 style='margin: 0; color: white; letter-spacing: 1px;'>ROGMUKTI DIAGNOSTIC CENTRE</h2>
            <p style='margin: 5px 0 0 0; font-size: 13px;'>Mollah stand, Auliapur, Patuakhali</p>
            <p style='margin: 2px 0 0 0; font-size: 12px;'>📞 Mobile: 01711867637</p>
        </div>
        
        <br>
        <table style='width: 100%; font-size: 14px; line-height: 1.6;'>
            <tr>
                <td><b>Invoice ID:</b> #{invoice_id}</td>
                <td style='text-align: right;'><b>Date:</b> {current_date[:10]}</td>
            </tr>
            <tr>
                <td><b>Patient Name:</b> {name}</td>
                <td style='text-align: right;'><b>Age:</b> {age} Y</td>
            </tr>
            <tr>
                <td><b>Mobile No:</b> {phone}</td>
                <td style='text-align: right;'><b>Ref. By:</b> {doctor}</td>
            </tr>
        </table>
        
        <br>
        <p><b>Test Description & Rate</b></p>
        <table style='width: 100%; border-collapse: collapse; font-size: 14px;'>
            <thead>
                <tr style='background-color: #f2f2f2;'>
                    <th style='border: 1px solid #ddd; padding: 8px; width: 10%;'>SL</th>
                    <th style='border: 1px solid #ddd; padding: 8px; text-align: left;'>Test Name</th>
                    <th style='border: 1px solid #ddd; padding: 8px; text-align: right; width: 25%;'>Price</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        
        <br>
        <table style='width: 100%; font-size: 14px; line-height: 1.6;'>
            <tr>
                <td style='width: 60%;'></td>
                <td style='text-align: right;'><b>Total Bill:</b> {total_amount:.2f} Tk</td>
            </tr>
            <tr>
                <td></td>
                <td style='text-align: right;'><b>Discount:</b> {discount_amount:.2f} Tk ({discount_pct}%)</td>
            </tr>
            <tr>
                <td></td>
                <td style='text-align: right;'><b>Advance Paid:</b> {advance_paid:.2f} Tk</td>
            </tr>
            <tr>
                <td></td>
                <td style='text-align: right; border-top: 1px dashed #1A3E6C; padding-top: 5px;'>
                    <span style='color: red; font-weight: bold; font-size: 16px;'>Due Amount: {due_amount:.2f} Tk</span>
                </td>
            </tr>
        </table>
        
        <br><br>
        <p style='text-align: center; font-size: 13px; color: gray; font-style: italic;'>Thank you for trusting us with your care.</p>
    </div>
    """,
    unsafe_allow_html=True
)
