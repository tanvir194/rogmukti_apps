import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="centered")

st.markdown("<h1 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Bazar, Auliapur, Patuakhali<br>Phone: 01711-867637</p>", unsafe_allow_html=True)

doctors_list = ["Select Doctor", "Self / Direct", "Dr. Saiful Islam RMP", "DR. Abdur Rahman D M F", "DR. Moshiur Rahman MBBS BCS FCPS"]

test_directory = {
    "Select Test": 0,
    "(CBC) + ESR": 600, "CBC": 350, "ESR": 250, "Platelet Count": 300,
    "MP": 500, "BT/CT": 350, "Blood Group & Rh": 200,
    "Random Blood Sugar": 200, "Fasting Blood Sugar": 200, "HbA1c": 1500,
    "T3": 1200, "T4": 1200, "TSH": 1100,
    "Lipid Profile": 1000, "USG of Whole Abdomen": 800,
    "USG Lower Abdomen": 750, "USG Pelvis": 700, "USG KUB": 750,
    "X-Ray Chest": 500, "ECG": 300, "Urine R/E": 250, "Stool R/E": 400
}

if 'sales_data' not in st.session_state:
    st.session_state['sales_data'] = pd.DataFrame(columns=["Invoice_No", "Date", "Patient", "Age", "Phone", "Doctor", "Total", "Discount", "Paid"])

tab1, tab2 = st.tabs(["📑 Billing / Cash Memo", "📊 Dashboard"])

with tab1:
    st.subheader("Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name:")
        age = st.text_input("Age:")
        phone = st.text_input("Phone Number:")
    with col2:
        ref_dr = st.selectbox("Referred By:", doctors_list)
        date_today = st.date_input("Date:", datetime.now())

    st.divider()
    st.subheader("🧪 Test Selection")
    
    total_amount = 0
    test_list_html = ""
    serial = 1
    
    for i in range(1, 6):
        test = st.selectbox(f"Test {i}:", list(test_directory.keys()), key=f"test{i}")
        if test != "Select Test":
            price = test_directory[test]
            st.write(f"✅ {test} = **{price} TK**")
            test_list_html += f"<tr><td style='padding:8px;'>{serial}</td><td style='padding:8px;'>{test}</td><td style='padding:8px; text-align:right;'>{price} TK</td></tr>"
            total_amount += price
            serial += 1

    discount = st.number_input("Discount (TK)", min_value=0, value=0, step=10)
    total_paid = total_amount - discount

    st.markdown(f"**Total Amount:** {total_amount} TK")
    st.markdown(f"**Discount:** {discount} TK")
    st.markdown(f"### **Net Payable:** {total_paid} TK")

    if st.button("💾 Save Invoice", type="primary"):
        if patient_name and ref_dr != "Select Doctor":
            today_str = datetime.now().strftime("%Y%m%d")
            invoice_no = f"ROG-{today_str}-{len(st.session_state['sales_data'])+1:03d}"
            
            new_row = pd.DataFrame([{
                "Invoice_No": invoice_no,
                "Date": date_today,
                "Patient": patient_name,
                "Age": age,
                "Phone": phone,
                "Doctor": ref_dr,
                "Total": total_amount,
                "Discount": discount,
                "Paid": total_paid
            }])
            st.session_state['sales_data'] = pd.concat([st.session_state['sales_data'], new_row], ignore_index=True)
            
            st.success(f"✅ Invoice Saved! Invoice No: **{invoice_no}**")
            
            memo_html = f"""
            <div style="font-family: Arial; max-width: 600px; margin: auto; padding: 40px; border: 4px solid black; background: white; color: black;">
                <h2 style="text-align: center; color: red;">ROGMUKTI DIAGNOSTIC CENTRE</h2>
                <p style="text-align: center;">Mollah Bazar, Auliapur, Patuakhali | 01711-867637</p>
                <p style="text-align: center; font-size: 11px; font-weight: bold; margin: 10px 0;">Invoice No: {invoice_no}</p>
                <hr>
                <table style="width:100%; font-size:15px;">
                    <tr><td><b>Patient:</b> {patient_name}</td><td style="text-align:right;"><b>Date:</b> {date_today}</td></tr>
                    <tr><td><b>Age:</b> {age}</td><td style="text-align:right;"><b>Doctor:</b> {ref_dr}</td></tr>
                </table>
                <hr>
                <table style="width:100%; border-collapse:collapse; font-size:15px;">
                    <tr style="background:#f0f0f0; font-weight:bold;">
                        <td style="padding:8px; width:40px;">Sl.</td>
                        <td style="padding:8px;">Test Name</td>
                        <td style="padding:8px; text-align:right;">Price</td>
                    </tr>
                    {test_list_html}
                </table>
                <hr>
                <table style="width:100%; font-weight:bold; font-size:17px;">
                    <tr><td style="text-align:right;">Total Amount:</td><td style="text-align:right;">{total_amount} TK</td></tr>
                    <tr><td style="text-align:right; color:red;">Discount:</td><td style="text-align:right; color:red;">{discount} TK</td></tr>
                    <tr style="font-size:19px; color:green;"><td style="text-align:right;">Net Payable:</td><td style="text-align:right;">{total_paid} TK</td></tr>
                </table>
                <p style="text-align:center; margin-top:30px;">Thank You!</p>
            </div>
            """
            st.components.v1.html(memo_html, height=580)
            st.markdown('<button onclick="window.print()" style="background:#28a745;color:white;padding:15px 30px;font-size:19px;border:none;border-radius:5px;width:100%;margin-top:15px;font-weight:bold;">🖨️ Print / Save as PDF</button>', unsafe_allow_html=True)
            
        else:
            st.error("Patient Name এবং Doctor সিলেক্ট করুন")

with tab2:
    st.header("📊 Dashboard")
    df = st.session_state['sales_data']
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        today = datetime.now().date()
        daily = df[df['Date'] == today]['Paid'].sum()
        weekly = df[df['Date'] >= (today - timedelta(days=7))]['Paid'].sum()
        monthly = df[df['Date'] >= today.replace(day=1)]['Paid'].sum()
        yearly = df[df['Date'].apply(lambda x: x.year) == today.year]['Paid'].sum()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Today", f"৳ {daily:,.0f}")
        c2.metric("Last 7 Days", f"৳ {weekly:,.0f}")
        c3.metric("This Month", f"৳ {monthly:,.0f}")
        c4.metric("This Year", f"৳ {yearly:,.0f}")
        
        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
    else:
        st.info("এখনো কোনো বিল তৈরি হয়নি।")

st.caption("Developed for Rogmukti Diagnostic Centre")
