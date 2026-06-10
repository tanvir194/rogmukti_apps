import streamlit as st
import sqlite3

# ================== লগইন চেক ==================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ আগে লগইন করুন")
    st.stop()

st.title("🖨️ মেডিকেল রিসিপ্ট প্রিন্ট")

# ================== ডাটাবেস কানেকশন ==================
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# ================== ইনভয়েস আইডি থেকে ডাটা নেওয়া ==================
invoice_id = st.query_params.get("invoice_id")  # অথবা সেশন থেকে নিতে পারো

if invoice_id:
    c.execute(f"SELECT * FROM billing_records WHERE id = ?", (invoice_id,))
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

        tests_list = selected_tests_data.split("|") if selected_tests_data else []

        # ================== প্রিন্ট বাটন ==================
        st.components.v1.html("""
            <button onclick="parent.window.print()" style="
                background-color: #1a365d; 
                color: white; 
                padding: 12px 30px;
                border: none; 
                border-radius: 5px;
                cursor: pointer; 
                font-weight: bold;
                width: 100%;
                height: 60px;
                font-size: 18px;">
                🖨️ রিসিপ্ট প্রিন্ট করুন (Print Now)
            </button>
        """, height=70)

        # ================== CSS + HTML রিসিপ্ট ==================
        st.markdown("""
        <style>
        @media print {
            body * { visibility: hidden; }
            #print-area, #print-area * { visibility: visible; }
            #print-area { 
                position: absolute; 
                left: 0; 
                top: 0; 
                width: 100%; 
                box-shadow: none; 
                margin: 0; 
            }
            @page { size: A4 portrait; margin: 15mm; }
        }

.receipt-container {
            border: 2px solid #1a365d;
            padding: 30px;
            border-radius: 8px;
            background-color: #ffffff;
            color: #000000;
            margin-top: 15px;
            max-width: 850px;
            margin-left: auto;
            margin-right: auto;
            font-family: Arial, sans-serif;
        }

        .receipt-header {
            text-align: center;
            background-color: #1a365d;
            color: #ffffff;
            padding: 20px;
            border-radius: 8px 8px 0 0;
        }

        .info-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
        .test-table { width: 100%; border-collapse: collapse; }
        .test-table th, .test-table td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left; 
        }
        .test-table th { 
            background-color: #3182ce; 
            color: #ffffff; 
            font-size: 17px; 
        }
        .summary-text { text-align: right; font-size: 18px; line-height: 1.8; margin-top: 20px; }
        </style>
        """, unsafe_allow_html=True)

        # টেবিল রো তৈরি
        table_rows = ""
        for item in tests_list:
            if ":" in item:
                try:
                    t_name, t_price = item.split(":", 1)
                    t_name = t_name.strip()
                    t_price_val = float(t_price.strip())
                except:
                    t_name = item.strip()
                    t_price_val = 0.0
            else:
                t_name = item.strip()
                t_price_val = 0.0

            table_rows += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; color: black;">{t_name}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right; color: black;">
                        {t_price_val:.2f}
                    </td>
                </tr>
            """

        receipt_body = f"""
        <div id="print-area" class="receipt-container">
            <div class="receipt-header">
                <h1 style="margin:0; font-size: 28px;">ROG MUKTI</h1>
                <p style="margin: 8px 0 0 0; font-size: 16px;">Mollah Stand, Auliapur, Patuakhali</p>
            </div>

            <table class="info-table">
                <tr>
                    <td style="padding: 8px; width: 50%;"><b>Bill No:</b> #{invoice_id}</td>
                    <td style="padding: 8px; text-align: right;"><b>Date:</b> {current_date}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><b>Patient Name:</b> {name}</td>
                    <td style="padding: 8px; text-align: right;"><b>Age:</b> {age} Years</td>
                </tr>
                <tr>
                    <td style="padding: 8px;"><b>Phone Number:</b> {phone}</td>
                    <td style="padding: 8px; text-align: right;"><b>Refd By:</b> {doctor}</td>
                </tr>
            </table>

            <table class="test-table">
                <thead>
                    <tr>
                        <th style="width: 70%;">Description (Test Name)</th>
                        <th style="text-align: right; width: 30%;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>

            <div class="summary-text">
                <p><b>Total Amount:</b> {total_amount:.2f} ৳</p>
                <p><b>Discount ({discount_pct}%):</b> -{discount_amount:.2f} ৳</p>
                <p><b>Advance Paid:</b> -{advance_paid:.2f} ৳</p>
                <p style="color: red; font-size: 22px; border-top: 2px solid #1a365d; padding-top: 10px;">
                    <b>Due Amount: {due_amount:.2f} ৳</b>
                </p>
            </div>
        </div>
        """

        st.markdown(receipt_body, unsafe_allow_html=True)

    else:
        st.error("কোনো বিল পাওয়া যায়নি")
else:
    st.info("কোনো বিল সিলেক্ট করা হয়নি। 'Patient Entry' পেজ থেকে বিল সিলেক্ট করে আসুন।")

