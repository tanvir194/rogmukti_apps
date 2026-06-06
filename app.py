import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# পেজ কনফিগারেশন
st.set_page_config(page_title="Rog Mukti Diagnostic Centre", layout="wide")

# ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic_final.db", check_same_thread=False)
c = conn.cursor()

# টেবিল তৈরি
c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    phone TEXT,
    doctor TEXT,
    tests TEXT,
    total_amount REAL,
    discount REAL,
    advance REAL,
    due REAL,
    date TEXT
)
""")
conn.commit()

# এখানে ১০০ থেকে ১৫০টি টেস্টের নাম ও দামের তালিকা (প্রয়োজনে আপনি আরও বাড়াতে পারবেন)
TEST_PRICES = {
    "CBC (Complete Blood Count)": 400.0,
    "Blood Sugar / Fasting": 100.0,
    "Serum Creatinine": 300.0,
    "ETT (Exercise Tolerance Test)": 3000.0,
    "USG of Whole Abdomen": 1500.0,
    "USG of Thyroid Gland": 1200.0,
    "Lipid Profile": 1000.0,
    "Liver Function Test (LFT)": 1200.0,
    "Serum Bilirubin": 250.0,
    "Urine R/E": 250.0,
    "HBsAg": 350.0,
    "Widal Test": 400.0,
    "Dengue NS1 Antigen": 600.0,
    "Blood Grouping & Rh Typing": 150.0,
    "X-Ray Chest P/A View": 500.0,
    "ECG (Electrocardiogram)": 400.0,
    "Troponin I": 1200.0,
    "Serum Electrolytes": 1000.0,
    "TSH (Thyroid Stimulating Hormone)": 600.0,
    "FT4 (Free Thyroxine)": 600.0,
    # এভাবে আপনি নিচে নতুন লাইন লিখে ১৫০+ টেস্ট সহজে যোগ করতে পারবেন...
}

def add_patient(name, age, phone, doctor, tests, total, discount, advance, due, date):
    c.execute('''
        INSERT INTO patients (name, age, phone, doctor, tests, total_amount, discount, advance, due, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, phone, doctor, tests, total, discount, advance, due, date))
    conn.commit)
    return c.lastrowid
st.sidebar.title("🧭 নেভিগেশন মেনু")
page = st.sidebar.radio("অপশন সিলেক্ট করুন:", ["নতুন পেশেন্ট এন্ট্রি", "পেশেন্ট ডাটাবেজ"])

if page == "নতুন পেশেন্ট এন্ট্রি":
    st.title("🏥 Rog Mukti Diagnostic Centre")
    st.markdown("---")
    
    if "receipt_data" not in st.session_state:
        st.session_state.receipt_data = None

    st.subheader("👤 পেশেন্ট এবং ডাক্তারের তথ্য")
    
    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name of the PT (পেশেন্টের নাম) *")
            age = st.number_input("Age (বয়স)", min_value=0, max_value=120, value=25)
            phone = st.text_input("Phone (মোবাইল নম্বর)")
        with col2:
            doctor_list = ["ডা. সাইদুল ইসলাম", "ডা. নাসরিন সুলতানা", "ডা. মোতালেব হোসেন", "Self / অন্যান্য"]
            doctor = st.selectbox("REFd By. Dr (ডাক্তার সিলেক্ট করুন)", doctor_list)
            date_input = st.date_input("Date (তারিখ)", datetime.now())
            date_str = date_input.strftime("%Y-%m-%d")
            
        st.markdown("---")
        st.subheader("🧪 টেস্ট এবং বিলিং সেকশন")
        
        # ড্রপডাউনে এখন সব টেস্ট আলফাবেটালি সাজানো থাকবে সার্চ করার সুবিধার্থে
        selected_tests = st.multiselect("Description (এখান থেকে টেস্ট সার্চ বা সিলেক্ট করুন)", sorted(list(TEST_PRICES.keys())))
        
        sub_total = sum(TEST_PRICES[test] for test in selected_tests)
        
        col3, col4 = st.columns(2)
        with col3:
            st.markdown(f"**টোটাল টেস্ট ফি:** {sub_total} টাকা")
            discount_pct = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
            advance = st.number_input("Advance (অগ্রিম পরিশোধ)", min_value=0.0, value=0.0, step=50.0)
        with col4:
            discount_amount = sub_total * (discount_pct / 100)
            due = sub_total - (discount_amount + advance)
            st.write(f"**Discount Amount:** {discount_amount} টাকা")
            st.metric(label="Due (বাকি)", value=f"{due} টাকা")

        submit_btn = st.form_submit_button("Save and Print Bill (ডাটা সেভ করুন)")
        
        if submit_btn:
            if name and selected_tests:
                tests_str = ", ".join(selected_tests)
                invoice_id = add_patient(name, age, phone, doctor, tests_str, sub_total, discount_pct, advance, due, date_str)
                
                st.session_state.receipt_data = {
                    "inv_no": f"{invoice_id:05d}",
                    "date": date_str,
                    "name": name,
                    "age": age,
                    "doctor": doctor,
                    "phone": phone,
                    "tests": selected_tests,
                    "total": sub_total,
                    "discount_pct": discount_pct,
                    "discount_amt": discount_amount,
                    "advance": advance,
                    "due": due
                }
                st.success("তথ্য ডাটাবেজে সেভ হয়েছে! নিচে রঙিন মানি রিসিট তৈরি হয়েছে।")
            elif not name:
                st.error("অনুগ্রহ করে পেশেন্টের নাম লিখুন।")
            elif not selected_tests:
                st.error("অনুগ্রহ করে অন্তত একটি টেস্ট সিলেক্ট করুন।")
    # রিসিট প্রিন্ট করার কালার ভিউ সেকশন
    if st.session_state.receipt_data:
        r = st.session_state.receipt_data
        st.markdown("---")
        st.subheader("📄 প্রাকদর্শন: রঙিন মানি রিসিট")
        
        # টেস্ট টেবিলের রোগুলো তৈরি করা
        table_rows = ""
        for i, test_name in enumerate(r['tests'], 1):
            table_rows += f"""
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 8px;">{i}</td>
                <td style="padding: 8px;">{test_name}</td>
                <td style="padding: 8px; text-align: right;">{TEST_PRICES[test_name]:.2f} ৳</td>
            </tr>
            """

        # সম্পূর্ণ রঙিন এইচটিএমএল স্ট্রাকচার
        html_receipt = f"""
        <div style="border: 3px solid #1e3a8a; padding: 25px; border-radius: 12px; background-color: #f8fafc; color: #1e293b; font-family: 'Segoe UI', Arial, sans-serif; max-width: 700px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            
            <!-- নীল রঙের প্রফেশনাল হেডার ব্যান্ড -->
            <div style="text-align: center; background-color: #1e3a8a; color: white; padding: 15px; border-radius: 8px 8px 0 0; margin: -25px -25px 20px -25px;">
                <h2 style="margin: 0; font-size: 26px; text-transform: uppercase; letter-spacing: 1px;">Rog Mukti Diagnostic Centre</h2>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Mollah Stand, Auliapur, Patuakhali</p>
                <p style="margin: 2px 0 0 0; font-size: 14px; font-weight: bold;">📞 Phone: 01711867637</p>
            </div>
            
            <div style="text-align: center; margin-bottom: 20px;">
                <span style="background-color: #e2e8f0; padding: 6px 20px; font-weight: bold; border-radius: 20px; color: #0f172a; font-size: 15px; letter-spacing: 1px;">MONEY RECEIPT</span>
            </div>
            
            <!-- পেশেন্ট ইনফো টেবিল -->
            <table style="width: 100%; font-size: 14px; margin-bottom: 20px; background: white; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <tr>
                    <td style="padding: 4px;"><b>Invoice No:</b> <span style="color:#1e3a8a; font-weight:bold;">{r['inv_no']}</span></td>
                    <td style="text-align: right; padding: 4px;"><b>Date:</b> {r['date']}</td>
                </tr>
                <tr>
                    <td style="padding: 4px;"><b>Patient Name:</b> {r['name']}</td>
                    <td style="text-align: right; padding: 4px;"><b>Age:</b> {r['age']} Years</td>
                </tr>
                <tr>
                    <td style="padding: 4px;"><b>Phone Number:</b> {r['phone']}</td>
                    <td style="text-align: right; padding: 4px;"><b>Refd By:</b> {r['doctor']}</td>
                </tr>
            </table>
            
            <!-- মেইন বিলিং টেবিল -->
            <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;">
                <thead>
                    <tr style="background-color: #3b82f6; color: white; font-size: 15px;">
                        <th style="text-align: left; padding: 10px; width: 10%;">SL</th>
                        <th style="text-align: left; padding: 10px; width: 65%;">Description (Test Name)</th>
                        <th style="text-align: right; padding: 10px; width: 25%;">Amount</th>
                    </tr>
                </thead>
                <tbody style="font-size: 14px;">
                    {table_rows}
                    <!-- ক্যালকুলেশন রো সমূহ -->
                    <tr style="background-color: #f1f5f9; font-weight: bold;">
                        <td></td>
                        <td style="text-align: right; padding: 8px;">Total Amount:</td>
                        <td style="text-align: right; padding: 8px;">{r['total']:.2f} ৳</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td style="text-align: right; padding: 8px; color: #475569;">Discount ({r['discount_pct']}%):</td>
                        <td style="text-align: right; padding: 8px; color: #475569;">- {r['discount_amt']:.2f} ৳</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td style="text-align: right; padding: 8px; color: #16a34a;">Advance Paid:</td>
                        <td style="text-align: right; padding: 8px; color: #16a34a;">{r['advance']:.2f} ৳</td>
                    </tr>
                    <tr style="background-color: #fee2e2; color: #b91c1c; font-weight: bold; font-size: 16px; border-top: 2px solid #f87171;">
                        <td></td>
                        <td style="text-align: right; padding: 10px;">Due (বাকি টাকা):</td>
                        <td style="text-align: right; padding: 10px;">{r['due']:.2f} ৳</td>
                    </tr>
                </tbody>
            </table>
            
            <!-- সিগনেচার এরিয়া -->
            <div style="margin-top: 60px; display: flex; justify-content: flex-end;">
                <div style="text-align: center; width: 150px;">
                    <hr style="border: none; border-top: 1px solid #475569; margin-bottom: 5px;">
                    <span style="font-size: 13px; font-weight: bold; color: #475569;">Authorized Signature</span>
                </div>
            </div>
        </div>
        """
        
        # স্ট্রীমলিটে সম্পূর্ণ কোডমুক্ত রঙিন ভিউ রেন্ডার করার কমান্ড
        st.components.v1.html(html_receipt, height=580, scrolling=True)
        st.info("💡 রিসিটটি প্রিন্ট করার জন্য মাউসের রাইট বাটন ক্লিক করে **Print** চাপুন অথবা কিবোর্ড থেকে **Ctrl + P** চাপুন।")

# পার্ট ৪: পেশেন্ট ডাটাবেজ ভিউ
elif page == "পেশেন্ট ডাটাবেজ":
    st.title("📋 রোগমুক্তি ক্লিনিক ডাটাবেজ")
    st.markdown("---")
    
    c.execute("SELECT * FROM patients ORDER BY id DESC")
    data = c.fetchall()
    
    if data:
        columns = ["INV ID", "পেশেন্টের নাম", "বয়স", "মোবাইল নম্বর", "রেফার্ড ডাক্তার", "সিলেক্টেড টেস্ট", "মোট বিল", "ছাড় (%)", "অগ্রিম জমা", "বাকি টাকা", "তারিখ"]
        df = pd.DataFrame(data, columns=columns)
        df["INV ID"] = df["INV ID"].apply(lambda x: f"{x:05d}")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("এখনো ডাটাবেজে কোনো পেশেন্টের তথ্য রেকর্ড করা হয়নি।")

