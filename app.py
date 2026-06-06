import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# পেজ কনফিগারেশন
st.set_page_config(page_title="Rog Mukti Diagnostic Centre", layout="wide")

# ডাটাবেজ কানেকশন (নতুন নাম দিয়ে সম্পূর্ণ রিসেট)
conn = sqlite3.connect("rogmukti_clinic_final.db", check_same_thread=False)
c = conn.cursor()

# পেশেন্ট টেবিল তৈরি
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

# টেস্টের নাম এবং দামের ডিকশনারি (আপনার প্রয়োজন মতো দাম পরিবর্তন করতে পারবেন)
TEST_PRICES = {
    "CBC (Complete Blood Count)": 400.0,
    "Hgb (Hemoglobin)": 150.0,
    "WBC Count": 200.0,
    "Platelet Count": 200.0,
    "ETT (Exercise Tolerance Test)": 3000.0,
    "USG of Thyroid Gland": 1200.0,
    "Blood Sugar": 100.0,
    "Sereat Creatinine": 300.0
}

# ডাটাবেজে তথ্য সেভ করার ফাংশন
def add_patient(name, age, phone, doctor, tests, total, discount, advance, due, date):
    c.execute('''
        INSERT INTO patients (name, age, phone, doctor, tests, total_amount, discount, advance, due, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, phone, doctor, tests, total, discount, advance, due, date))
    conn.commit()
    return c.lastrowid # সদ্য সেভ হওয়া ইনভয়েস নম্বর রিটার্ন করবে
# সাইডবার মেনু
st.sidebar.title("🧭 নেভিগেশন মেনু")
page = st.sidebar.radio("অপশন সিলেক্ট করুন:", ["নতুন পেশেন্ট এন্ট্রি", "পেশেন্ট ডাটাবেজ"])

if page == "নতুন পেশেন্ট এন্ট্রি":
    st.title("🏥 Rog Mukti Diagnostic Centre")
    st.markdown("---")
    
    # সেশন স্টেট তৈরি (রিসিট দেখানোর জন্য)
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
        
        # টেস্ট সিলেক্ট করার ড্রপডাউন
        selected_tests = st.multiselect("Description (এখান থেকে টেস্ট সার্চ বা সিলেক্ট করুন)", list(TEST_PRICES.keys()))
        
        # সিলেক্ট করা টেস্টের ভিত্তিতে অটোমেটিক সাব-টোটাল হিসাব
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

        # সেভ এবং প্রিন্ট বাটন
        submit_btn = st.form_submit_button("Save and Print Baton (ডাটা সেভ করুন)")
        
        if submit_btn:
            if name and selected_tests:
                tests_str = ", ".join(selected_tests)
                # ডাটাবেজে সেভ করে আইডি জেনারেট করা
                invoice_id = add_patient(name, age, phone, doctor, tests_str, sub_total, discount_pct, advance, due, date_str)
                
                # রিসিটে দেখানোর জন্য তথ্য সেশন স্টেটে রাখা
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
                st.success("তথ্য সফলভাবে ডাটাবেজে সেভ হয়েছে! নিচে ক্যাশ মেমো তৈরি হয়েছে।")
            elif not name:
                st.error("অনুগ্রহ করে পেশেন্টের নাম লিখুন।")
            elif not selected_tests:
                st.error("অনুগ্রহ করে অন্তত একটি টেস্ট সিলেক্ট করুন।")
    # যদি ডাটা সেভ হয়ে থাকে তবে ক্যাশ মেমো দেখাবে
    if st.session_state.receipt_data:
        r = st.session_state.receipt_data
        st.markdown("---")
        
        # মানি রিসিটের মূল বক্স (বর্ডারসহ)
        with st.container():
            st.markdown(
                f"""
                <div style="border: 2px solid #000; padding: 20px; border-radius: 10px; background-color: #fff; color: #000; font-family: 'Courier New', Courier, monospace;">
                    <div style="text-align: center; line-height: 1.2;">
                        <h2 style="margin: 0; color: #000;">Rog Mukti Diagnostic Centre</h2>
                        <p style="margin: 5px 0;">Mollah Stand, Auliapur</p>
                        <p style="margin: 5px 0;">Patuakhali</p>
                        <p style="margin: 5px 0;"><b>Phone: 01711867637</b></p>
                        <hr style="border-top: 2px dashed #000; margin: 10px 0;">
                        <h3 style="margin: 5px 0; letter-spacing: 2px; color: #000;">MONEY RECEIPT</h3>
                    </div>
                    
                    <table style="width: 100%; margin-top: 15px; font-size: 14px; color: #000;">
                        <tr>
                            <td><b>INV No:</b> {r['inv_no']}</td>
                            <td style="text-align: right;"><b>Date:</b> {r['date']}</td>
                        </tr>
                        <tr>
                            <td colspan="2"><b>Name of the PT:</b> {r['name']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Age:</b> {r['age']} Years</td>
                        </tr>
                        <tr>
                            <td colspan="2"><b>Phone:</b> {r['phone']}</td>
                        </tr>
                        <tr>
                            <td colspan="2"><b>Refd By. Dr:</b> {r['doctor']}</td>
                        </tr>
                    </table>
                    
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px; color: #000;">
                        <thead>
                            <tr style="border-top: 1px solid #000; border-bottom: 1px solid #000;">
                                <th style="text-align: left; padding: 5px; width: 10%;">SL</th>
                                <th style="text-align: left; padding: 5px; width: 65%;">Description</th>
                                <th style="text-align: right; padding: 5px; width: 25%;">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                """, unsafe_allow_html=True
            )
            
            # টেস্টগুলোর রো তৈরি করা
            for i, test_name in enumerate(r['tests'], 1):
                st.markdown(
                    f"""
                            <tr style="font-size: 14px;">
                                <td style="padding: 5px; color: #000;">{i}</td>
                                <td style="padding: 5px; color: #000;">{test_name}</td>
                                <td style="text-align: right; padding: 5px; color: #000;">{TEST_PRICES[test_name]:.2f}</td>
                            </tr>
                    """, unsafe_allow_html=True
                )
                
            st.markdown(
                f"""
                            <tr style="border-top: 1px solid #000;">
                                <td></td>
                                <td style="text-align: right; padding: 5px; font-weight: bold;">Total Amount =</td>
                                <td style="text-align: right; padding: 5px; font-weight: bold;">{r['total']:.2f}</td>
                            </tr>
                            <tr>
                                <td></td>
                                <td style="text-align: right; padding: 5px;">Discount ({r['discount_pct']}%) =</td>
                                <td style="text-align: right; padding: 5px;">{r['discount_amt']:.2f}</td>
                            </tr>
                            <tr>
                                <td></td>
                                <td style="text-align: right; padding: 5px;">Advance =</td>
                                <td style="text-align: right; padding: 5px;">{r['advance']:.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #000;">
                                <td></td>
                                <td style="text-align: right; padding: 5px; font-weight: bold;">Due =</td>
                                <td style="text-align: right; padding: 5px; font-weight: bold;">{r['due']:.2f}</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <div style="margin-top: 50px; text-align: right;">
                        <span style="border-top: 1px solid #000; padding-top: 5px;"><b>Signature</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
            
            st.write("💡 কম্পিউটারে প্রিন্ট করার জন্য **Ctrl + P** চাপুন এবং Layout 'Portrait' সিলেক্ট করুন।")

# পার্ট ৪: ডাটাবেজ ভিউ (সব রেকর্ড দেখার জন্য)
elif page == "পেশেন্ট ডাটাবেজ":
    st.title("📋 রোগমুক্তি ক্লিনিক ডাটাবেজ")
    st.markdown("---")
    
    c.execute("SELECT * FROM patients ORDER BY id DESC")
    data = c.fetchall()
    
    if data:
        columns = ["INV ID", "পেশেন্টের নাম", "বয়স", "মোবাইল নম্বর", "রেফার্ড ডাক্তার", "সিলেক্টেড টেস্ট", "মোট বিল", "ছাড় (%)", "অগ্রিম জমা", "বাকি টাকা", "তারিখ"]
        df = pd.DataFrame(data, columns=columns)
        # ইনভয়েস আইডি ফরম্যাট করা (যেমন: 00001)
        df["INV ID"] = df["INV ID"].apply(lambda x: f"{x:05d}")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("এখনো ডাটাবেজে কোনো পেশেন্টের তথ্য রেকর্ড করা হয়নি।")
        
