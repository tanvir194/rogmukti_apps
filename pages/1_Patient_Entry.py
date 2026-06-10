import streamlit as st
import sqlite3
from datetime import datetime

# ১. সিকিউরিটি চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

# ২. ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS billing_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT,
    age INTEGER,
    phone TEXT,
    doctor TEXT,
    selected_tests TEXT,
    total_amount REAL,
    discount_percent REAL,
    net_paid REAL,
    due_amount REAL,
    billing_date TEXT
)
""")
conn.commit()

st.title("📝 টেস্ট এবং বিলিং সেকশন")

# ফর্ম ছাড়া সরাসরি ইনপুট (যাতে লাইভ আপডেট হয়)
st.subheader("পেশেন্ট ইনফরমেশন")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("পেশেন্টের নাম (Name of the PT) *")
    phone = st.text_input("মোবাইল নম্বর (Phone)")
with col2:
    age = st.number_input("বয়স (Age)", min_value=1, max_value=120, value=25)
    doctor = st.selectbox("ডাক্তার সিলেক্ট করুন (Refd By)", ["ডা. সাইদুল ইসলাম", "অন্যান্য"])

st.markdown("---")
st.subheader("টেস্ট সিলেকশন")

# 📌 টেস্টের নাম ও প্রাইস তালিকা
test_prices = {
    "Urine Pregnancy Test (HCG)": 200.0,
    "AFP (Alpha Fetoprotein)": 1200.0,
    "Blood Sugar (RBS / Fasting)": 200.0,
    "Anti-HCV": 600.0
}

# ড্রপডাউনে অপশন সিলেক্ট
selected_tests = st.multiselect("টেস্ট সিলেক্ট করুন (Description):", list(test_prices.keys()))

# 💥 ম্যাজিক: টেস্ট সিলেক্ট করার সাথে সাথে এখানে লাইভ যোগ হবে
total_fee = sum(test_prices[test] for test in selected_tests)
st.info(f"📋 লাইভ টোটাল ফি: {total_fee} টাকা")

st.markdown("---")
st.subheader("পেমেন্ট ও ডিসকাউন্ট")
col3, col4 = st.columns(2)
with col3:
    discount_pct = st.number_input("ডিসকাউন্ট (Discount %)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
    advance_paid = st.number_input("অগ্রিম পরিশোধ (Advance Paid)", min_value=0.0, value=0.0, step=50.0)

# 💥 ম্যাজিক: ডিসকাউন্ট বা অ্যাডভান্স লেখার সাথে সাথে লাইভ হিসাব হবে
discount_amount = (total_fee * discount_pct) / 100.0
net_payable = total_fee - discount_amount
due_amount = net_payable - advance_paid

with col4:
    st.metric("ডিসকাউন্ট প্রদেয় (টাকা)", f"{discount_amount} ৳")
    st.metric("মোট বাকি টাকা (Due)", f"{due_amount} ৳")

st.markdown("---")
# আলাদাভাবে নিচে সেভ বাটন
submit_button = st.button("Save Bill and Generate Receipt (ডাটা সেভ করুন)")

# ডাটা সেভ লজিক
if submit_button:
    if not name or not selected_tests:
        st.error("⚠️ পেশেন্টের নাম এবং অন্তত একটি টেস্ট সিলেক্ট করা বাধ্যতামূলক!")
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        tests_str = ", ".join(selected_tests)
        
        c.execute("""
            INSERT INTO billing_records (patient_name, age, phone, doctor, selected_tests, total_amount, discount_percent, net_paid, due_amount, billing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, age, phone, doctor, tests_str, total_fee, discount_pct, advance_paid, due_amount, current_date))
        conn.commit()
        
        st.success("✅ সফলভাবে ডাটা সেভ হয়েছে!")
        st.balloons()
        
        # মানি রিসিট ভিউ
        st.subheader("📄 মানি রিসিট")
        receipt_html = f"""
        <div style="border: 2px solid #1a365d; padding: 20px; border-radius: 10px; font-family: sans-serif; background-color: white; color: black;">
            <div style="text-align: center; background-color: #1a365d; color: white; padding: 10px; border-radius: 5px;">
                <h2>ROG MUKTI DIAGNOSTIC CENTRE</h2>
                <p>Mollah Stand, Auliapur, Patuakhali<br>Phone: 01711867637</p>
            </div>
            <div style="margin-top: 15px; display: flex; justify-content: space-between;">
                <div>
                    <p><b>Patient Name:</b> {name}</p>
                    <p><b>Phone Number:</b> {phone}</p>
                </div>
                <div style="text-align: right;">
                    <p><b>Date:</b> {current_date}</p>
                    <p><b>Age:</b> {age} Years</p>
                    <p><b>Refd By:</b> {doctor}</p>
                </div>
            </div>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr style="background-color: #3182ce; color: white; text-align: left;">
                    <th style="padding: 8px;">Description (Test Name)</th>
                    <th style="padding: 8px; text-align: right;">Amount</th>
                </tr>
                {"".join([f"<tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'>{t}</td><td style='padding: 8px; border-bottom: 1px solid #ddd; text-align: right;'>{test_prices[t]} ৳</td></tr>" for t in selected_tests])}
            </table>
            <div style="margin-top: 20px; text-align: right; font-size: 16px;">
                <p><b>Total Amount:</b> {total_fee} ৳</p>
                <p><b>Discount ({discount_pct}%):</b> -{discount_amount} ৳</p>
                <p><b>Advance Paid:</b> {advance_paid} ৳</p>
                <p style="color: red; font-size: 18px;"><b>Due (বাকি টাকা): {due_amount} ৳</b></p>
            </div>
        </div>
        """
        st.markdown(receipt_html, unsafe_allow_html=True)

conn.close()
