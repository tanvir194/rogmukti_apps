import sys
import os
import streamlit as st
import sqlite3

sys.path.append(".")
from sidebar_monitor import show_live_sidebar
show_live_sidebar()

# Security or login check
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("⚠️ Please login first.")
    st.stop()

st.title("🖨️ English Money Receipt")
st.write("---------------------- Invoice ID Lookup ----------------------")

# ইউজার ম্যানুয়ালি বিল নম্বর দিয়ে সার্চ করতে পারবেন
invoice_id = st.number_input("Enter Bill No / Invoice ID to Print:", min_value=0, step=1, value=0)

# যদি আগের পেজ থেকে অটোমেটিক আইডি আসে, তবে সরাসরি ওটাই লোড হবে
if invoice_id == 0 and "last_invoice_id" in st.session_state:
    invoice_id = st.session_state.last_invoice_id

if invoice_id > 0:
    # Fix Directory Path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "rogmukti_clinic_fix.db")
    
    # Database Connection
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM billing_records WHERE ID = ?", (invoice_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        # Assign variables from database row index
        name = row[1]
        age = row[2]
        phone = row[3]
        doctor = row[4]
        selected_tests_data = row[5]
        
        # দশমিক বাদ দিয়ে সরাসরি পূর্ণসংখ্যায় (Integer) রূপান্তর
        total_amount = int(row[6])
        discount_amount = int(row[7])  # সরাসরি ডাটাবেজ থেকে ডিসকাউন্টের টাকা
        advance_paid = int(row[8])
        due_amount = int(row[9])
        current_date = row[10]
        
        # Split selected tests by pipe '|' symbol
        tests_list = [item.strip() for item in selected_tests_data.split('|') if item.strip()]
        
        # Create Dynamic HTML Table Rows for Tests
        table_rows = ""
        for index, item in enumerate(tests_list, start=1):
            if ":" in item:
                t_name, t_price = item.split(":", 1)
            else:
                t_name, t_price = item, "0"
            
            try:
                t_price_val = int(float(t_price))
            except:
                t_price_val = 0
                
            table_rows += f"""
            <tr>
                <td style="text-align: center;">{index}</td>
                <td>{t_name}</td>
                <td style="text-align: right;">{t_price_val} Tk</td>
            </tr>
            """
            
        # 🧾 Full HTML, CSS and Print Logic
        full_html_page = f"""
        <style>
            .receipt-box {{
                max-width: 450px;
                margin: 20px auto;
                padding: 25px;
                border: 2px solid #1a365d;
                border-radius: 12px;
                background-color: white;
                color: black;
                font-family: 'Arial', sans-serif;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .receipt-header {{
                text-align: center;
                border-bottom: 2px dashed #1a365d;
                padding-bottom: 12px;
                margin-bottom: 15px;
            }}
            .receipt-header h3 {{
                margin: 0;
                color: #1a365d;
                font-size: 20px;
                letter-spacing: 0.5px;
            }}
            .receipt-header p {{
                margin: 4px 0;
                font-size: 13px;
                color: #4a5568;
            }}
            .info-table {{
                width: 100%;
                font-size: 13px;
                margin-bottom: 15px;
                line-height: 1.6;
            }}
            .info-table td {{
                padding: 2px 0;
            }}
            .items-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
                margin-bottom: 15px;
            }}
            .items-table th {{
                border-top: 1px solid black;
                border-bottom: 1px solid black;
                padding: 6px 4px;
                font-weight: bold;
            }}
            .items-table td {{
                padding: 6px 4px;
                border-bottom: 1px dashed #e2e8f0;
            }}
            .calculation-section {{
                width: 100%;
                font-size: 14px;
                margin-top: 10px;
                border-top: 1px solid black;
                padding-top: 8px;
                line-height: 1.6;
            }}
            .calculation-section td {{
                padding: 3px 0;
            }}
            .footer-text {{
                text-align: center;
                font-size: 12px;
                color: #718096;
                margin-top: 25px;
                border-top: 1px dashed #cbd5e0;
                padding-top: 10px;
            }}
            @media print {{
                body * {{
                    visibility: hidden;
                }}
                .receipt-box, .receipt-box * {{
                    visibility: visible;
                }}
                .receipt-box {{
                    position: absolute;
                    left: 0;
                    top: 0;
                    width: 100%;
                    border: none;
                    box-shadow: none;
                    margin: 0;
                    padding: 0;
                }}
            }}
        </style>
        
        <div class="receipt-box">
            <div class="receipt-header">
                <h3>ROGMUKTI DIAGNOSTIC CENTRE</h3>
                <p>Mollah stand, Auliapur, Patuakhali</p>
                <p>Mobile: 01711867637</p>
            </div>
            
            <table class="info-table">
                <tr>
                    <td style="width: 50%;"><b>Invoice ID:</b> #{invoice_id}</td>
                    <td style="text-align: right; width: 50%;"><b>Date:</b> {current_date}</td>
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
            
            <p style="font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #1a365d;">Test Description & Rate</p>
            <table class="items-table">
                <thead>
                    <tr>
                        <th style="width: 10%; text-align: center;">SL</th>
                        <th style="width: 65%; text-align: left;">Test Name</th>
                        <th style="width: 25%; text-align: right;">Price</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            
            <table class="calculation-section">
                <tr>
                    <td style="width: 60%;"></td>
                    <td style="width: 20%; text-align: left;">Total Bill:</td>
                    <td style="width: 20%; text-align: right; font-weight: bold;">{total_amount} Tk</td>
                </tr>
                <tr>
                    <td></td>
                    <td style="text-align: left;">Discount:</td>
                    <td style="text-align: right; font-weight: bold; color: green;">{discount_amount} Tk</td>
                </tr>
                <tr>
                    <td></td>
                    <td style="text-align: left;">Advance Paid:</td>
                    <td style="text-align: right; font-weight: bold; color: blue;">{advance_paid} Tk</td>
                </tr>
                <tr style="font-size: 15px; border-top: 1px dashed black;">
                    <td></td>
                    <td style="text-align: left; padding-top: 5px;"><b>Due Amount:</b></td>
                    <td style="text-align: right; color: {'red' if due_amount > 0 else 'black'}; padding-top: 5px;"><b>{due_amount} Tk</b></td>
                </tr>
            </table>
            
            <div class="footer-text">
                Thank you for trusting us with your care.
            </div>
        </div>
        """
        
        # স্ক্রিনে রিসিটটি দেখানোর ব্যবস্থা
        st.markdown(full_html_page, unsafe_allow_html=True)
        
        # রিসিট প্রিন্ট করার বাটন
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🖨️ Print Money Receipt Now", on_click=None)
        
    else:
        st.error("❌ No record found for this Invoice ID.")
