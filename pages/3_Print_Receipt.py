import streamlit as st
import sqlite3

# লগইন চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ আগে লগইন করুন")
    st.stop()

st.title("🖨️ মেডিকেল রিসিপ্ট প্রিন্ট")

# ================== invoice_id নেওয়ার চেষ্টা (একাধিক উপায়) ==================
invoice_id = None

# 1. Query Params থেকে (URL)
if "invoice_id" in st.query_params:
    invoice_id = st.query_params.get("invoice_id")

# 2. Session State থেকে (সবচেয়ে নির্ভরযোগ্য)
if not invoice_id and "current_invoice_id" in st.session_state:
    invoice_id = st.session_state.current_invoice_id

# 3. URL থেকে সরাসরি (যদি অন্যভাবে আসে)
if not invoice_id:
    try:
        invoice_id = st.query_params["invoice_id"]
    except:
        pass

# ================== ডাটাবেস ও রিসিপ্ট ==================
if invoice_id:
    conn = sqlite3.connect("rogmukti_clinic_fix.db")
    c = conn.cursor()
    
    c.execute("SELECT * FROM billing_records WHERE id = ?", (invoice_id,))
    row = c.fetchone()
    conn.close()

    if row:
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
        st.components.v1.html(f"""
            <button onclick="parent.window.print()" style="
                background-color: #1a365d; color: white; padding: 12px 30px;
                border: none; border-radius: 5px; cursor: pointer; font-weight: bold;
                width: 100%; height: 60px; font-size: 18px;">
                🖨️ রিসিপ্ট প্রিন্ট করুন (Print Now)
            </button>
        """, height=80)

        # CSS
        st.markdown("""<style>
        @media print {
            body * { visibility: hidden; }
            #print-area, #print-area * { visibility: visible; }
            #print-area { position: absolute; left: 0; top: 0; width: 100%; }
            @page { size: A4 portrait; margin: 15mm; }
        }
        .receipt-container { border: 2px solid #1a365d; padding: 30px; border-radius: 8px; 
            background: white; max-width: 850px; margin: 20px auto; font-family: Arial, sans-serif; }
        .receipt-header { text-align: center; background: #1a365d; color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 10px; }
        th { background: #3182ce; color: white; }
        .summary { text-align: right; font-size: 18px; margin-top: 20px; }
        </style>""", unsafe_allow_html=True)

        # Test Rows
        table_rows = ""
        for item in tests_list:
            if ":" in item:
                t_name, t_price = item.split(":", 1)
                t_name = t_name.strip()
                try:
                    t_price_val = float(t_price.strip())
                except:
                    t_price_val = 0.0
            else:
                t_name = item
                t_price_val = 0.0

            table_rows += f"""
            <tr>
                <td>{t_name}</td>
                <td style="text-align:right;">{t_price_val:.2f}</td>
            </tr>"""

        # Receipt Body
        receipt_body = f"""
        <div id="print-area" class="receipt-container">
            <div class="receipt-header">
                <h1 style="margin:0;">ROG MUKTI</h1>
                <p style="margin:5px 0;">Mollah Stand, Auliapur, Patuakhali</p>
            </div>
            
            <table>
                <tr><td><b>Bill No:</b> #{invoice_id}</td><td style="text-align:right;"><b>Date:</b> {current_date}</td></tr>
                <tr><td><b>Patient Name:</b> {name}</td><td style="text-align:right;"><b>Age:</b> {age} Years</td></tr>
                <tr><td><b>Phone:</b> {phone}</td><td style="text-align:right;"><b>Refd By:</b> {doctor}</td></tr>
            </table>

            <table style="margin-top:20px;">
                <thead><tr><th>Description</th><th style="text-align:right;">Amount</th></tr></thead>
                <tbody>{table_rows}</tbody>
            </table>

            <div class="summary">
                <p><b>Total Amount:</b> {total_amount:.2f} ৳</p>
                <p><b>Discount ({discount_pct}%):</b> -{discount_amount:.2f} ৳</p>
                <p><b>Advance Paid:</b> -{advance_paid:.2f} ৳</p>
                <p style="color:red; font-size:22px; border-top:2px solid #1a365d; padding-top:8px;">
                    <b>Due Amount: {due_amount:.2f} ৳</b>
                </p>
            </div>
        </div>
        """
        st.markdown(receipt_body, unsafe_allow_html=True)

    else:
        st.error(f"ID #{invoice_id} এর বিল পাওয়া যায়নি")
        
else:
    st.info("কোনো বিল সিলেক্ট করা হয়নি। 'Patient Entry' পেজ থেকে বিল সিলেক্ট করে আসুন।")
    st.write("**Debug Info:**")
    st.write("Query Params:", dict(st.query_params))
    st.write("Session State Keys:", list(st.session_state.keys()))
