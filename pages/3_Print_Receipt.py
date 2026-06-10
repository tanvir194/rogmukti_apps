import streamlit as st
import sqlite3

# সিকিউরিটি বা লগইন চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ আগে লগইন করুন।")
    st.stop()

st.title("🏥 মেডিকেল রিসিট প্রিন্ট")
st.write("------------------- Invoice ID তথ্য -------------------")

invoice_id = None

# কুয়েরি প্যারামিটার অথবা সেশন স্টেট থেকে ইনভয়েস আইডি রিড করা
if "invoice_id" in st.query_params:
    invoice_id = st.query_params.get("invoice_id")
elif "last_invoice_id" in st.session_state:
    invoice_id = st.session_state.last_invoice_id

if not invoice_id:
    st.info("💡 কোনো ইনভয়েস আইডি পাওয়া যায়নি। অনুগ্রহ করে 'Patient Entry' পেজ থেকে তথ্য সাবমিট করুন।")
    st.stop()

# ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

c.execute("SELECT * FROM billing_records WHERE id = ?", (invoice_id,))
row = c.fetchone()
conn.close()

if not row:
    st.error(f"❌ ID #{invoice_id} এর কোনো রেকর্ড পাওয়া যায়নি।")
    st.stop()

# ডাটাবেজের কলাম ইনডেক্স সিরিয়াল অনুযায়ী ভেরিয়েবল অ্যাসাইন
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

# লজিক্যাল হিসাব পুনরায় করা
discount_amount = (total_amount * discount_pct) / 100.0

# পাইপ '|' চিহ্ন দিয়ে আলাদা করে টেস্টের লিস্ট তৈরি করা
tests_list = [item.strip() for item in selected_tests_data.split('|') if item.strip()]

# ------------------- ব্রাউজার প্রিন্ট বোতাম -------------------
st.components.v1.html("""
    <button onclick="parent.window.print()" style="
        background-color: #1a365d; 
        color: white; 
        padding: 14px 30px; 
        border: none; 
        border-radius: 8px; 
        cursor: pointer; 
        font-size: 18px; 
        font-weight: bold; 
        width: 100%; 
        height: 55px;
    ">
        🖨️ রিসিট প্রিন্ট করুন (Print Now)
    </button>
""", height=80)

# ------------------- সিএসএস স্টাইল (CSS Style) -------------------
st.markdown("""
<style>
@media print {
    body * {
        visibility: hidden;
    }
    #receipt, #receipt * {
        visibility: visible;
    }
    #receipt {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
    }
    @page {
        size: A4 portrait;
        margin: 10mm;
    }
}

.receipt-box {
    max-width: 600px;
    margin: 20px auto;
    padding: 30px;
    border: 2px solid #1a365d;
    border-radius: 12px;
    background-color: white;
    font-family: Arial, sans-serif;
    color: black;
}
.header {
    text-align: center;
    background-color: #1a365d;
    color: white;
    padding: 20px;
    border-radius: 8px 8px 0 0;
    margin-bottom: 20px;
}
.header h2 {
    margin: 0;
    font-size: 24px;
}
.info-table, .test-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
    color: black;
}
.info-table td {
    padding: 6px 0;
    font-size: 15px;
}
.test-table th, .test-table td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
    font-size: 14px;
}
.test-table th {
    background-color: #f2f2f2;
}
.total-section {
    text-align: right;
    font-size: 16px;
    line-height: 1.6;
}
.total-section b {
    color: #1a365d;
}
</style>
""", unsafe_allow_html=True)

# ------------------- ডাইনামিক রসিদ জেনারেটর -------------------
receipt_html = f"""
<div id="receipt" class="receipt-box">
    <div class="header">
        <h2>রোগমুক্তি ক্লিনিক</h2>
        <p style="margin: 5px 0 0 0;">রোগীর অফিশিয়াল মানি রিসিট</p>
    </div>
    
    <table class="info-table">
        <tr>
            <td><b>ইনভয়েস আইডি:</b> #{invoice_id}</td>
            <td style="text-align: right;"><b>তারিখ:</b> {current_date}</td>
        </tr>
        <tr>
            <td><b>রোগীর নাম:</b> {name}</td>
            <td style="text-align: right;"><b>বয়স:</b> {age}</td>
        </tr>
        <tr>
            <td><b>মোবাইল:</b> {phone}</td>
            <td style="text-align: right;"><b>ডাক্তার:</b> {doctor}</td>
        </tr>
    </table>
    
    <h3 style="color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 5px; font-size: 16px;">টেস্ট ও রেট বিবরণী</h3>
    <table class="test-table">
        <thead>
            <tr>
                <th style="width: 10%;">নং</th>
                <th style="width: 65%;">টেস্টের নাম</th>
                <th style="width: 25%; text-align: right;">মূল্য (টাকা)</th>
            </tr>
        </thead>
        <tbody>
"""

# টেস্টের নাম ও দাম আলাদা করে টেবিলে যোগ করা
for index, item in enumerate(tests_list, start=1):
    if ":" in item:
        t_name, t_price = item.split(":", 1)
    else:
        t_name, t_price = item, "0.0"
        
    receipt_html += f"""
            <tr>
                <td>{index}</td>
                <td>{t_name}</td>
                <td style="text-align: right;">{float(t_price):.2f} ৳</td>
            </tr>
    """

receipt_html += f"""
        </tbody>
    </table>
    
    <div class="total-section">
        <p>মোট বিল (Total): {total_amount:.2f} ৳</p>
        <p>ছাড় (Discount): {discount_amount:.2f} ৳ ({discount_pct}%)</p>
        <p>অগ্রিম পরিশোধ (Paid): <b>{advance_paid:.2f} ৳</b></p>
        <p style="font-size: 18px; border-top: 1px dashed #1a365d; padding-top: 5px; margin-top: 5px;">
            <b>বাকি টাকা (Due Amount): <span style="color: red;">{due_amount:.2f} ৳</span></b>
        </p>
    </div>
    
    <div style="margin-top: 25px; text-align: center; font-size: 12px; color: #555; border-top: 1px solid #eee; padding-top: 10px;">
        <p>আমাদের ওপর আস্থা রাখার জন্য ধন্যবাদ।</p>
    </div>
</div>
"""
# --- কোডের একেবারে শেষ লাইনে st.markdown-এর পরিবর্তে এটি লিখুন ---

# CSS স্টাইল এবং HTML কন্টেন্টকে একসাথে জোড়া দেওয়া হচ্ছে
full_html_content = f"""
<style>
/* প্রিন্ট করার সময় শুধু রসিদের অংশটি দেখানোর জন্য মিডিয়া কুয়েরি */
@media print {{
    body * {{
        visibility: hidden !important;
    }}
    #receipt, #receipt * {{
        visibility: visible !important;
    }}
    #receipt {{
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
    }}
    @page {{
        size: A4 portrait;
        margin: 10mm;
    }}
}}

/* স্ক্রিনে রসিদটি যেভাবে দেখাবে */
.receipt-box {{
    max-width: 600px;
    margin: 10px auto;
    padding: 30px;
    border: 2px solid #1a365d;
    border-radius: 12px;
    background-color: white;
    font-family: 'Arial', sans-serif;
    color: black;
}}
.header {{
    text-align: center;
    background-color: #1a365d;
    color: white;
    padding: 20px;
    border-radius: 8px 8px 0 0;
    margin-bottom: 20px;
}}
.header h2 {{
    margin: 0;
    font-size: 24px;
}}
.info-table, .test-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
    color: black;
}}
.info-table td {{
    padding: 6px 0;
    font-size: 15px;
}}
.test-table th, .test-table td {{
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
    font-size: 14px;
}}
.test-table th {{
    background-color: #f2f2f2;
}}
.total-section {{
    text-align: right;
    font-size: 16px;
    line-height: 1.6;
}}
.total-section b {{
    color: #1a365d;
}}
</style>

{receipt_html}
"""

# নিখুঁতভাবে HTML রেন্ডার করার কম্পোনেন্ট (উচ্চতা ১০০০ পিক্সেল দেওয়া হয়েছে যেন পুরো রসিদ ধরে)
st.components.v1.html(full_html_content, height=1000, scroller=True)
