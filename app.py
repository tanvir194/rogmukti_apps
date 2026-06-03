import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="centered")

# সফটওয়্যার হেডার
st.markdown("<h2 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Bazar, Auliapur, Patuakhali<br>Phone: 01711867637</p>", unsafe_allow_html=True)

# ট্যাব সিস্টেম
tab1, tab2 = st.tabs(["📑 Billing / Cash Memo", "📊 Admin Dashboard"])

# গুগল শিট থেকে ডেটা লোড করার লিংক
SHEET_ID = "1BwMbaLP4koABhxaxrGGBq8I5AYmn9BDAu7evJ6TiUl4"
csv_url = f"https://google.com{SHEET_ID}/export?format=csv&gid=1152917726"

@st.cache_data(ttl=10)
def load_data_from_excel():
    test_dict = {"Select Test": 0}
    doc_list = ["Select Doctor"]
    try:
        df = pd.read_csv(csv_url, header=None)
        for idx, row in df.iterrows():
            if idx == 0: continue
            if len(row) > 2:
                test_name = str(row[1]).strip()
                price_val = row[2]
                if test_name and test_name != "nan" and test_name != "" and "Column" not in test_name and "Category" not in test_name:
                    try: price = int(float(price_val))
                    except: price = 0
                    test_dict[test_name] = price
            if len(row) > 5:
                doc_name = str(row[5]).strip()
                if doc_name and doc_name != "nan" and doc_name != "" and "Column" not in doc_name and "Self" not in doc_name:
                    if doc_name not in doc_list: doc_list.append(doc_name)
    except: pass
    if len(test_dict) <= 1:
        test_dict = {"Select Test": 0, "(CBC) + ESR": 600, "Widal Test": 450, "T3": 1200, "Urine R/E": 250, "USG": 800}
    if len(doc_list) <= 1:
        doc_list.extend(["Dr. Saiful Islam RMP", "DR. Abdur Rahman D M F", "DR. Moshiur Rahman MBBS BCS FCPS"])
    if "Self / Direct" not in doc_list: doc_list.append("Self / Direct")
    return test_dict, doc_list

test_directory, doctors_list = load_data_from_excel()

if 'sales_data' not in st.session_state:
    st.session_state['sales_data'] = pd.DataFrame(columns=["Date", "Patient", "Doctor", "Total", "Discount", "Paid"])

# --- ট্যাব ১: বিলিং সেকশন ---
with tab1:
    st.markdown("<h3 style='text-align: center; background-color: #007ff5; color: white; padding: 5px; border-radius: 5px;'>CASH MEMO</h3>", unsafe_allow_html=True)
    
    st.subheader("Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Name of The PT:", key="p_name")
        age = st.text_input("AGE:", key="p_age")
    with col2:
        ref_dr = st.selectbox("Reff. By Dr:", doctors_list, key="p_doc")
        date_today = st.date_input("Date:", datetime.now(), key="p_date")

    st.divider()
    st.subheader("Services / Test Selection")
    total_amount = 0
    selected_tests_list = []
    for i in range(1, 6):
        test_name = st.selectbox(f"Select Test {i}:", list(test_directory.keys()), key=f"test_{i}")
        if test_name != "Select Test":
            price = test_directory[test_name]
            st.text(f"Price: {price} TK")
            selected_tests_list.append(f"<li>{test_name}: {price} TK</li>")
            total_amount += price

    st.divider()
    st.subheader("Bill Calculation")
    discount = st.number_input("Discount (TK):", min_value=0, value=0, step=5)
    total_paid = total_amount - discount

    st.markdown(f"#### **Total Amount:** {total_amount} TK")
    st.markdown(f"#### **Discount:** <span style='color:red;'>{discount} TK</span>", unsafe_allow_html=True)
    st.markdown(f"### **Total PAID:** <span style='color:green;'>{total_paid} TK</span>", unsafe_allow_html=True)

    if st.button("Generate & Save Invoice", type="primary"):
        if patient_name == "":
            st.error("দয়া করে রোগীর নাম লিখুন!")
        elif ref_dr == "Select Doctor":
            st.error("দয়া করে ডাক্তার সিলেক্ট করুন!")
        else:
            new_bill = pd.DataFrame([{
                "Date": date_today, "Patient": patient_name, "Doctor": ref_dr,
                "Total": total_amount, "Discount": discount, "Paid": total_paid
            }])
            st.session_state['sales_data'] = pd.concat([st.session_state['sales_data'], new_bill], ignore_index=True)
            st.success(f"Invoice generated and saved successfully!")
            
            # প্রিন্ট করার জন্য জাভাস্ক্রিপ্ট বাটন ট্রিকস
            st.markdown("<br><hr><h4 style='text-align:center;'>--- PRINT PREVIEW ---</h4>", unsafe_allow_html=True)
            memo_html = f"""
            <div style="border: 2px solid #000; padding: 15px; border-radius: 5px; font-family: Arial;">
                <h2 style="text-align: center; color: red; margin:0;">ROGMUKTI DIAGNOSTIC CENTRE</h2>
                <p style="text-align: center; margin: 2px;">Mollah Bazar, Auliapur, Patuakhali</p>
                <hr>
                <p><b>Patient Name:</b> {patient_name} &nbsp;&nbsp;&nbsp;&nbsp; <b>Age:</b> {age}</p>
                <p><b>Ref. Doctor:</b> {ref_dr} &nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> {date_today}</p>
                <hr>
                <h4>Tests:</h4>
                <ul>{"".join(selected_tests_list)}</ul>
                <hr>
                <p align="right"><b>Total Amount:</b> {total_amount} TK</p>
                <p align="right" style="color:red;"><b>Discount:</b> {discount} TK</p>
                <p align="right" style="color:green; font-size:18px;"><b>Total PAID:</b> {total_paid} TK</p>
            </div>
            <br>
            <button onclick="window.print()" style="background-color: #4CAF50; color: white; padding: 10px 24px; font-size: 16px; border: none; border-radius: 4px; cursor: pointer; width: 100%;">🖨️ Click Here to Print / Save PDF</button>
            """
            st.components.v1.html(memo_html, height=450, scrolling=True)

# --- ট্যাব ২: অ্যাডমিন ড্যাশবোর্ড ---
with tab2:
    st.header("📊 Clinic Accounts Summary")
    df_sales = st.session_state['sales_data']
    if not df_sales.empty:
        df_sales['Date'] = pd.to_datetime(df_sales['Date']).dt.date
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    
    daily_sales = df_sales[df_sales['Date'] == today]['Paid'].sum() if not df_sales.empty else 0
    weekly_sales = df_sales[df_sales['Date'] >= start_of_week]['Paid'].sum() if not df_sales.empty else 0
    monthly_sales = df_sales[df_sales['Date'] >= start_of_month]['Paid'].sum() if not df_sales.empty else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Daily Cash", f"{daily_sales} TK")
    c2.metric("Weekly Cash", f"{weekly_sales} TK")
    c3.metric("Monthly Cash", f"{monthly_sales} TK")
    
    st.divider()
    st.header("🩺 Doctor's Referral Fee (30%)")
    selected_doc = st.selectbox("Select Doctor to see Fee:", doctors_list[1:])
    if not df_sales.empty:
        doc_bills = df_sales[df_sales['Doctor'] == selected_doc]
        total_doc_business = doc_bills['Paid'].sum()
        total_commission = total_doc_business * 0.30
        col_d1, col_d2 = st.columns(2)
        col_d1.subheader(f"Total Bill: {total_doc_business} TK")
        col_d2.markdown(f"<h3>Doctor Fee: <span style='color:orange;'>{total_commission} TK</span></h3>", unsafe_allow_html=True)
        
