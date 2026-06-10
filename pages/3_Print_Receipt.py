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


# ------------------- ডাইনামিক রসিদের সম্পূর্ণ HTML ও CSS জেনারেটর -------------------
# এখানে পাইথনের f-string ফরমেটিং এর ঝামেলা এড়াতে আমরা একদম ফ্রেশ HTML ব্লক তৈরি করছি

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
        
    table_rows += f"""
    <tr>
        <td>{index}</td>
        <td>{t_name}</td>
        <td style="text-align: right;">{t_price_val:.2f} ৳</td>
    </tr>
    """
    full_html_page = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@media print {{
    body {{
        background: white;
        color: black;
    }}
    /* প্রিন্ট করার সময় শুধু রসিদের অংশটি দেখানোর জন্য মিডিয়া কুয়েরি */
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

.receipt-box {{
    max-width: 550px;
    margin: 10px auto;
    padding: 25px;
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
    padding: 15px;
    border-radius: 8px 8px 0 0;
    margin-bottom: 20px;
}}
.header h2 {{
    margin: 0;
    font-size: 22px;
}}
.header p {{
    margin: 5px 0 0 0;
    font-size: 14px;
}}
.info-table, .test-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
    color: black;
}}
.info-table td {{
    padding: 5px 0;
    font-size: 14px;
}}
.test-table th, .test-table td {{
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
    font-size: 13px;
}}
.test-table th {{
    background-color: #f2f2f2;
}}
.total-section {{
    text-align: right;
    font-size: 15px;
    line-height: 1.6;
}}
.total-section b {{
    color: #1a365d;
}}
</style>
</head>
<body>

<div id="receipt" class="receipt-box">
    <div class="header">
        <h2>রোগমুক্তি ক্লিনিক</h2>
        <p>রোগীর অফিশিয়াল মানি রিসিট</p>
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
    
    <h3 style="color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 5px; font-size: 15px; margin-top: 10px;">টেস্ট ও রেট বিবরণী</h3>
    <table class="test-table">
        <thead>
            <tr>
                <th style="width: 10%;">নং</th>
                <th style="width: 65%;">টেস্টের নাম</th>
                <th style="width: 25%; text-align: right;">মূল্য (টাকা)</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    
    <div class="total-section">
        <p>মোট বিল (Total): {total_amount:.2f} ৳</p>
        <p>ছাড় (Discount): {discount_amount:.2f} ৳ ({discount_pct}%)</p>
        <p>অগ্রিম পরিশোধ (Paid): <b>{advance_paid:.2f} ৳</b></p>
        <p style="font-size: 16px; border-top: 1px dashed #1a365d; padding-top: 5px; margin-top: 5px;">
            <b>বাকি টাকা (Due Amount): <span style="color: red;">{due_amount:.2f} ৳</span></b>
        </p>
    </div>
    
    <div style="margin-top: 20px; text-align: center; font-size: 12px; color: #555; border-top: 1px solid #eee; padding-top: 10px;">
        <p>আমাদের ওপর আস্থা রাখার জন্য ধন্যবাদ।</p>
    </div>
</div>

</body>
</html>
"""

# এবার স্ট্রিক্টলি st.components.v1.html এর মাধ্যমে কোনো এরর বা টেক্সট লিক ছাড়া রেন্ডার হবে
st.components.v1.html(full_html_page, height=750)
