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

# ডাটাবেজে তথ্য সেভ করার ফাংশন
def add_patient(name, age, phone, doctor, tests, total, discount, advance, due, date):
    c.execute('''
        INSERT INTO patients (name, age, phone, doctor, tests, total_amount, discount, advance, due, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, phone, doctor, tests, total, discount, advance, due, date))
    conn.commit()
    return c.lastrowid
    
# ক্রমিক নম্বরসহ টেস্টের নাম এবং স্ট্যান্ডার্ড দামের তালিকা
TEST_PRICES = {
    # --- Haematology ---
    "01. CBC (Complete Blood Count)": 600.0,
    "06. MP": 200.0,
    "07. BT/CT": 350.0,
    "08. C/E Count": 250.0,

    # --- Serology ---
    "09. Widal": 450.0,
    "10. Aso Titre": 450.0,
    "11. CRP": 450.0,
    "12. RA/RF": 450.0,
    "13. HBs Ag (Screen Test)": 450.0,
    "14. TPHA": 450.0,
    "15. VDRL": 400.0,
    "16. Group & Rh Factor": 200.0,
    "17. Mantaux-Test (M.T)": 300.0,
    "18. Triple Antigen": 850.0,
    "19. R.Fever": 450.0,
    "20. HIV": 500.0,
    "21. HCV": 500.0,
    "22. TB (ICT)": 750.0,
    "23. Malaria. pf/pv": 700.0,
    "24. H. Pylori": 850.0,
    "25. Fallarlia (ICT)": 750.0,
    "26. Dengue NS1.": 300.0,
    "17. Dengue IgG/IGM.": 300.0,

    # --- Hormone Pannel ---
    "27. T3": 1200.0,
    "28. T4": 1200.0,
    "29. FT3": 900.0,
    "30. FT4": 900.0,
    "31. TSH": 1100.0,
    "32. HbA1c": 1500.0,
    "33. Prolactin": 1200.0,
    "34. S. IgE": 1500.0,
    "20. S.IgE (Device Test)": 700.0,

    # --- Bio Chemical Analysis ---
    "11. Random": 200.0,
    "12. Fasting": 200.0,
    "38. 2hr. After Breakfast": 200.0,
    "39. 2hr. After 75gm Glucose": 200.0,
    "40. O.G.T.T": 500.0,
    "41. Blood Urea": 400.0,
    "42. Cholesterol": 350.0,
    "43. HDL": 400.0,
    "44. TG": 350.0,
    "45. LDL": 300.0,
    "46. S.GPT(ALT)": 500.0,
    "47. S.GOT(AST)": 500.0,
    "15. Bilirubin Total": 350.0,
    "49. Lipid Profile": 1000.0,
    "16. Bilirubin Direct/Indirect": 450.0,
    "18. Serum Creatinine": 400.0,
    "52. Uric Acid": 400.0,
    "53. Amylase": 700.0,
    "54. Calcium": 600.0,

    # --- Urine & Stool Exam ---
    "02. Urine Pregnancy Test (PT)": 200.0,
    "01. Urine R/E": 250.0,
    "03. Stool R/E": 400.0,
    "04. Stool OBT": 400.0,

    # --- UI Ultrasound Imaging ---
    "01. USG Whole Abdomen": 1000.0,
    "02. USG Upper Abdomen": 800.0,
    "03. USG Lower Abdomen": 800.0,
    "04. USG KUB": 1000.0,
    "05. USG Pregnancy Profile": 800.0,
    "06. USG Breast": 1200.0
}  # <--- এই ক্লোজিং ব্র্যাকেটটি দেওয়া জরুরি ছিল

# সাইডবার মেনু নেভিগেশন
st.sidebar.title("🧭 নেভিগেশন মেনু")
page = st.sidebar.radio("অপশন সিলেক্ট করুন:", ["নতুন পেশেন্ট এন্ট্রি", "পেশেন্ট ডাটাবেজ"])

if page == "নতুন পেশেন্ট এন্ট্রি":
    if "custom_tests" not in st.session_state:
        st.session_state.custom_tests = {}

    if "receipt_data" not in st.session_state:
        st.session_state.receipt_data = None

    st.subheader("👤 পেশেন্ট এবং ডাক্তারের তথ্য")
    
    # রোগীর সাধারণ তথ্যের আলাদা ফর্ম
    with st.form("patient_info_form"):
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
        
        info_submit = st.form_submit_button("পেশেন্ট তথ্য নিশ্চিত করুন")

    st.markdown("---")
    st.subheader("🧪 টেস্ট এবং বিলিং সেকশন")
    
    # ফর্মের বাইরে স্বাধীন টেস্ট ড্রপডাউন (লাইভ কাউন্টারের জন্য)
    selected_tests = st.multiselect("Description (এখান থেকে টেস্ট সার্চ বা সিলেক্ট করুন)", sorted(list(TEST_PRICES.keys())))
      # --- কাস্টম টেস্ট যোগ করার ইউআই ---
    
    st.markdown("### ➕ তালিকার বাইরের কাস্টম টেস্ট")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        custom_name = st.text_input("কাস্টম টেস্টের নাম লিখুন:", key="c_name_input")
    with c_col2:
        custom_price = st.number_input("টেস্টের রেট (টাকা):", min_value=0.0, step=50.0, key="c_price_input")

    if custom_name:
        st.session_state.custom_tests[custom_name] = float(custom_price)

        st.session_state.custom_tests = {}
        st.rerun()

    # --- সিলেক্টেড টেস্ট এবং কাস্টম টেস্টের নাম ও দাম একসাথে করা ---
    all_selected_tests = list(selected_tests)  # ড্রপডাউন থেকে সিলেক্ট করা স্ট্যান্ডার্ড টেস্ট
    total_bill = sum(TEST_PRICES.get(t, 0.0) for t in selected_tests)  # স্ট্যান্ডার্ড টেস্টের মোট দাম

    # কাস্টম টেস্টগুলো যোগ করা
    for name, price in st.session_state.custom_tests.items():
        all_selected_tests.append(name)
        total_bill += price
  
    custom_test_active = "Custom Test / অন্যান্য (নিচে নাম ও দাম লিখুন)" in selected_tests
    custom_name = ""
    custom_price = 0.0
    
    if custom_test_active:
        st.info("💡 কাস্টম টেস্টের ফিল্ড সচল হয়েছে। নিচে নাম ও দাম লিখুন।")
    # লাইভ কাউন্টার ক্যালকুলেশন (স্ট্যান্ডার্ড + কাস্টম টেস্টের দাম)
    sub_total = sum(TEST_PRICES.get(test, 0.0) for test in selected_tests)
    for c_name, c_price in st.session_state.custom_tests.items():
        sub_total += c_price

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"### 🧮 লাইভ টোটাল ফি: `{sub_total}` টাকা")
        discount_pct = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, step=1.0)
        advance = st.number_input("Advance (অগ্রিম পরিশোধ)", min_value=0.0, step=50.0)
        
    with col4:
        discount_amount = sub_total * (discount_pct / 100.0)
        due = sub_total - (discount_amount + advance)
        st.write(f"**ডিসকাউন্ট প্রদেয়:** {discount_amount} টাকা")
        st.metric(label="Due (মোট বাকি টাকা)", value=f"{due} টাকা")

            invoice_id = add_patient(name, age, phone, doctor, tests_str, sub_total, discount_amount, advance, due, date_str)
            
            receipt_tests = []
            for test in selected_tests:
                price = TEST_PRICES.get(test, 0.0)
                receipt_tests.append({"name": test, "price": price})
                
            for c_name, c_price in st.session_state.custom_tests.items():
                receipt_tests.append({"name": c_name, "price": c_price})

            st.session_state.receipt_data = {
                "inv_no": f"{invoice_id:05d}",
                "date": date_str,
                "name": name,
                "age": age,
                "doctor": doctor,
                "phone": phone,
                "tests": receipt_tests,
                "total": sub_total,
                "discount_pct": discount_pct,
                "discount_amt": discount_amount,
                "advance": advance,
                "due": due
            }
            
            st.session_state.custom_tests = {}
            st.success("সফলভাবে ডাটা সেভ হয়েছে! নিচে প্রিন্ট বাটন এবং মানি রিসিট প্রস্তুত।")
            st.rerun()
            
        elif not name:
            st.error("অনুগ্রহ করে ওপরের ফর্মে পেশেন্টের নাম লিখুন।")
        elif not selected_tests and not st.session_state.custom_tests:
            st.error("অনুগ্রহ করে অন্তত একটি টেস্ট সিলেক্ট বা যোগ করুন।")
            st.rerun()
            
        elif not name:
            st.error("অনুগ্রহ করে ওপরের ফর্মে পেশেন্টের নাম লিখুন।")
        elif not selected_tests and not st.session_state.custom_tests:
            st.error("অনুগ্রহ করে অন্তত একটি টেস্ট সিলেক্ট বা যোগ করুন।")

    if st.session_state.receipt_data:
        r = st.session_state.receipt_data
        st.markdown("---")
        
        # টেবিলের রো জেনারেশন
        table_rows = ""
        for i, item in enumerate(r['tests'], 1):
            table_rows += f"""
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 8px; color: #1e293b;">{i}</td>
                <td style="padding: 8px; color: #1e293b;">{item['name']}</td>
                <td style="padding: 8px; text-align: right; color: #1e293b;">{item['price']:.2f} ৳</td>
            </tr>
            """

        # সম্পূর্ণ রিসিটের রঙিন এইচটিএমএল স্ট্রাকচার (প্রিন্ট আইডি 'printArea' সহ)
        html_receipt = f"""
        <div id="printArea" style="border: 3px solid #1e3a8a; padding: 25px; border-radius: 12px; background-color: #f8fafc; font-family: 'Segoe UI', Arial, sans-serif; max-width: 650px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <div style="text-align: center; background-color: #1e3a8a; color: white; padding: 15px; border-radius: 8px 8px 0 0; margin: -25px -25px 20px -25px;">
                <h2 style="margin: 0; font-size: 24px; text-transform: uppercase; letter-spacing: 1px;">Rog Mukti Diagnostic Centre</h2>
                <p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">Mollah Stand, Auliapur, Patuakhali</p>
                <p style="margin: 2px 0 0 0; font-size: 13px; font-weight: bold;">📞 Phone: 01711867637</p>
            </div>
            
            <div style="text-align: center; margin-bottom: 15px;">
                <span style="background-color: #e2e8f0; padding: 5px 18px; font-weight: bold; border-radius: 20px; color: #0f172a; font-size: 14px; letter-spacing: 1px;">MONEY RECEIPT</span>
            </div>
            
            <table style="width: 100%; font-size: 13px; margin-bottom: 15px; background: white; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <tr>
                    <td style="padding: 4px; color: #1e293b;"><b>Invoice No:</b> <span style="color:#1e3a8a; font-weight:bold;">{r['inv_no']}</span></td>
                    <td style="text-align: right; padding: 4px; color: #1e293b;"><b>Date:</b> {r['date']}</td>
                </tr>
                <tr>
                    <td style="padding: 4px; color: #1e293b;"><b>Patient Name:</b> {r['name']}</td>
                    <td style="text-align: right; padding: 4px; color: #1e293b;"><b>Age:</b> {r['age']} Years</td>
                </tr>
                <tr>
                    <td style="padding: 4px; color: #1e293b;"><b>Phone Number:</b> {r['phone']}</td>
                    <td style="text-align: right; padding: 4px; color: #1e293b;"><b>Refd By:</b> {r['doctor']}</td>
                </tr>
            </table>
            
            <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;">
                <thead>
                    <tr style="background-color: #3b82f6; color: white; font-size: 14px;">
                        <th style="text-align: left; padding: 8px; width: 10%;">SL</th>
                        <th style="text-align: left; padding: 8px; width: 65%;">Description (Test Name)</th>
                        <th style="text-align: right; padding: 8px; width: 25%;">Amount</th>
                    </tr>
                </thead>
                <tbody style="font-size: 13px;">
                    {table_rows}
                    <tr style="background-color: #f1f5f9; font-weight: bold;">
                        <td></td>
                        <td style="text-align: right; padding: 8px; color: #1e293b;">Total Amount:</td>
                        <td style="text-align: right; padding: 8px; color: #1e293b;">{r['total']:.2f} ৳</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td style="text-align: right; padding: 6px; color: #475569;">Discount ({r['discount_pct']}%):</td>
                        <td style="text-align: right; padding: 6px; color: #475569;">- {r['discount_amt']:.2f} ৳</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td style="text-align: right; padding: 6px; color: #16a34a;">Advance Paid:</td>
                        <td style="text-align: right; padding: 6px; color: #16a34a;">{r['advance']:.2f} ৳</td>
                    </tr>
                    <tr style="background-color: #fee2e2; color: #b91c1c; font-weight: bold; font-size: 15px; border-top: 2px solid #f87171;">
                        <td></td>
                        <td style="text-align: right; padding: 8px;">Due (বাকি টাকা):</td>
                        <td style="text-align: right; padding: 8px;">{r['due']:.2f} ৳</td>
                    </tr>
                </tbody>
            </table>
            
            <div style="margin-top: 50px; display: flex; justify-content: flex-end;">
                <div style="text-align: center; width: 150px;">
                    <hr style="border: none; border-top: 1px solid #475569; margin-bottom: 5px;">
                    <span style="font-size: 12px; font-weight: bold; color: #475569;">Authorized Signature</span>
                </div>
            </div>
        </div>
        """

        # জাভাস্ক্রিপ্ট কোড যুক্ত নতুন উইন্ডো দিয়ে সরাসরি প্রিন্ট বাটন ব্যবস্থা
        st.subheader("📄 মানি রিসিট কন্ট্রোল")
        
        # ক্লিক করলেই রিসিটের অংশটুকু প্রিন্ট করার জাভাস্ক্রিপ্ট যুক্ত বাটন
        print_button_html = f"""
        <script>
        function printInvoice() {{
            var printContents = document.getElementById('printArea').innerHTML;
            var originalContents = document.body.innerHTML;
            document.body.innerHTML = printContents;
            window.print();
            document.body.innerHTML = originalContents;
            window.location.reload();
        }}
        </script>
        <button onclick="printInvoice()" style="background-color: #1e3a8a; color: white; padding: 12px 24px; font-size: 16px; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; width: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
            🖨️ প্রিন্ট করুন (Print Receipt)
        </button>
        <br><br>
        {html_receipt}
        """
        
        # স্ট্রীমলিটে সম্পূর্ণ বাটন ও রিসিট রেন্ডার করা
        st.components.v1.html(print_button_html, height=720, scrolling=True)

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
    
