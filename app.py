import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests

def send_sms(mobile_number, message):
    api_url = "https://greenweb.com.bd"
    api_token = "YOUR_API_TOKEN_HERE" 
    payload = {'token': api_token, 'to': mobile_number, 'message': message}
    try:
        response = requests.post(api_url, data=payload, timeout=5)
        return response.status_code == 200
    except:
        return False
        
st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="centered")

# সফটওয়্যার হেডার
st.markdown("<h2 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Bazar, Auliapur, Patuakhali<br>Phone: 01711867637</p>", unsafe_allow_html=True)

# ট্যাব সিস্টেম
tab1, tab2 = st.tabs(["📑 Billing / Cash Memo", "📊 Admin Dashboard"])

# --- ১00% ফিক্সড ডেটাবেজ (সরাসরি কোডের ভেতর আপনার শিটের সব প্রধান টেস্ট ও ডাক্তার) ---
doctors_list = [
    "Select Doctor", "Self / Direct", "Dr. Saiful Islam RMP", 
    "DR. Abdur Rahman D M F", "DR. Moshiur Rahman MBBS BCS FCPS"
]

test_directory = {
    "Select Test": 0,
    "(CBC) + ESR": 600, "Widal Test": 450, "T.A Test": 1050, "Platelet Count": 300,
    "MP": 500, "BT/CT": 350, "C/E Count": 250, "T3": 1200, "T4": 1200, "FT3": 900,
    "FT4": 900, "TSH": 1100, "HbA1c": 1500, "Prolactin": 1200, "S. IgE": 1500,
    "Aso Titre": 450, "CRP": 450, "RA/RF": 450, "HBs Ag (Screen Test)": 450,
    "TPHA": 450, "VDRL": 400, "Group & Rh Factor": 200, "Mantoux-Test (M.T)": 350,
    "Triple Antigen": 1050, "R.Fever": 650, "HIV": 600, "HCV": 600, "TB (ICT)": 750,
    "Malaria p/l/p/v": 700, "H. Pylori": 850, "Filaria (ICT)": 750, "Dengue NS1, IgG/IgM": 300,
    "Random Blood Sugar": 200, "Fasting Blood Sugar": 200, "2hr After Breakfast": 200,
    "2hr After 75gm Glucose": 200, "O.G.T.T": 500, "Blood Urea": 400, "Cholesterol": 350,
    "HDL": 400, "TG": 350, "LDL": 300, "S.GPT(ALT)": 500, "S.GOT(AST)": 500,
    "Bilirubin Total": 350, "Lipid Profile": 1000, "Bilirubin Direct/Indirect": 450,
    "Serum Creatinine": 300, "Uric Acid": 400, "Amylase": 700, "Calcium": 500,
    "X-Ray Chest": 500, "X-Ray PNS": 500, "X-Ray Maxila": 500, "X-Ray Nasopharynx": 550,
    "X-Ray Abdomen A/P": 500, "X-Ray Cervical Spine": 600, "Plane X-Ray Abdomen": 500,
    "X-Ray Skull": 600, "X-Ray Pelvic": 500, "X-Ray Mandible A/P": 550, "X-Ray KUB": 500,
    "USG of Whole Abdomen": 800, "ECG": 300, "Urine Pregnancy Test (PT)": 200,
    "Urine R/E": 250, "Stool R/E": 400, "Stool OBT": 400
}

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
            selected_tests_list.append(f"<tr style='border-bottom: 1px solid #ddd;'><td style='padding: 8px;'>{test_name}</td><td style='padding: 8px; text-align: right;'>{price} TK</td></tr>")
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
                "Date": date_today, "Patient": patient_name,
                "Total": total_amount, "Discount": discount
            }])
            st.session_state['sales_data'] = pd.concat([st.session_state['sales_data'], new_bill], ignore_index=True)
            st.success(f"Invoice generated and saved successfully for {patient_name}!")
            
            # 📱 এখানে অটোমেটিক SMS পাঠানোর কোড যুক্ত করা হলো
            if patient_phone:  
                sms_text = f"প্রিয় {patient_name}, রোগমুক্তি ডায়াগনস্টিক সেন্টারে আপনার ইনভয়েস তৈরি হয়েছে। মোট বিল: {total_paid} টাকা। ধন্যবাদ।"
                sms_status = send_sms(patient_phone, sms_text)
                if sms_status:
                    st.info("রোগীর মোবাইলে কনফার্মেশন SMS পাঠানো হয়েছে।")
                else:
                    st.warning("বিল সেভ হয়েছে, কিন্তু SMS পাঠানো যায়নি (টোকেন চেক করুন)।")
        
            
            # একদম ঝকঝকে সাদা প্রফেশনাল মেমো ডিজাইন (ডার্ক মোডেও কালো হবে না)
            memo_html = f"""
            <div style="background-color: white; color: black; border: 2px solid #000; padding: 20px; border-radius: 5px; font-family: Arial, sans-serif; max-width: 500px; margin: auto;">
                <h2 style="text-align: center; color: red; margin:0; font-size: 22px; font-weight: bold;">ROGMUKTI DIAGNOSTIC CENTRE</h2>
                <p style="text-align: center; margin: 4px; font-size: 14px; font-weight: bold; color: #333;">Mollah Bazar, Auliapur, Patuakhali<br>Phone: 01711867637</p>
                <div style="background-color: #007ff5; color: white; text-align: center; padding: 5px; margin: 10px 0; font-weight: bold; font-size: 16px; border-radius: 3px;">CASH MEMO</div>
                <table style="width: 100%; font-size: 14px; border-collapse: collapse; color: black;">
                    <tr><td style="padding: 3px;"><b>Patient Name:</b> {patient_name}</td><td style="padding: 3px; text-align: right;"><b>Age:</b> {age}</td></tr>
                    <tr><td style="padding: 3px;"><b>Ref. Doctor:</b> {ref_dr}</td><td style="padding: 3px; text-align: right;"><b>Date:</b> {date_today}</td></tr>
                </table>
                <hr style="border-top: 1px solid black;">
                <table style="width: 100%; font-size: 14px; border-collapse: collapse; color: black;">
                    <tr style="background-color: #f2f2f2; font-weight: bold;"><td style="padding: 8px;">Test Description</td><td style="padding: 8px; text-align: right;">Amount</td></tr>
                    {"".join(selected_tests_list)}
                </table>
                <hr style="border-top: 1px solid black; margin-top: 20px;">
                <table style="width: 100%; font-size: 15px; color: black; font-weight: bold;">
                    <tr><td style="text-align: right; padding: 3px;">Total Amount:</td><td style="text-align: right; width: 100px; padding: 3px;">{total_amount} TK</td></tr>
                    <tr><td style="text-align: right; padding: 3px; color: red;">Discount:</td><td style="text-align: right; padding: 3px; color: red;">{discount} TK</td></tr>
                    <tr style="font-size: 18px; color: green;"><td style="text-align: right; padding: 5px;">Total PAID:</td><td style="text-align: right; padding: 5px; border-top: 2px double green;">{total_paid} TK</td></tr>
                </table>
                <p style="else: center; font-size: 12px; margin-top: 3px; color: #555;"><i>Thank you for choosing us!</i></p>
            </div>
            <br>
            <button onclick="window.print()" style="background-color: #4CAF50; color: white; padding: 12px 24px; font-size: 16px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-weight: bold;">🖨️ Click Here to Print / Save PDF</button>
            """
            st.components.v1.html(memo_html, height=520, scrolling=True)

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
        if not doc_bills.empty:
            st.write("Patient List:")
            st.dataframe(doc_bills[["Date", "Patient", "Paid"]])
            
