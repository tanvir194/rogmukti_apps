import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="centered")

# হেডার
st.markdown("<h2 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Bazar, Auliapur, Patuakhali<br>Phone: 01711-867637</p>", unsafe_allow_html=True)

doctors_list = ["Select Doctor", "Self / Direct", "Dr. Saiful Islam RMP", "DR. Abdur Rahman D M F", "DR. Moshiur Rahman MBBS BCS FCPS"]

test_directory = {
    "Select Test": 0, "(CBC) + ESR": 600, "Widal Test": 450, "T.A Test": 1050, "Platelet Count": 300,
    "MP": 500, "BT/CT": 350, "T3": 1200, "T4": 1200, "TSH": 1100, "HbA1c": 1500,
    "Random Blood Sugar": 200, "Fasting Blood Sugar": 200, "Lipid Profile": 1000,
    "USG of Whole Abdomen": 800, "X-Ray Chest": 500, "Urine R/E": 250, "ECG": 300
}

if 'sales_data' not in st.session_state:
    st.session_state['sales_data'] = pd.DataFrame(columns=["Date", "Patient", "Age", "Doctor", "Total", "Discount", "Paid"])

tab1, tab2 = st.tabs(["📑 Billing", "📊 Dashboard"])

with tab1:
    st.markdown("<h3 style='text-align: center; background-color: #007ff5; color: white; padding: 8px;'>CASH MEMO</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name:")
        age = st.text_input("Age:")
        phone = st.text_input("Phone Number:")
    with col2:
        ref_dr = st.selectbox("Referred By:", doctors_list)
        date_today = st.date_input("Date:", datetime.now())

    st.divider()
    total_amount = 0
    selected_tests = []
    
    for i in range(1, 6):
        test = st.selectbox(f"Test {i}:", list(test_directory.keys()), key=f"t{i}")
        if test != "Select Test":
            price = test_directory[test]
            st.write(f"✅ {test} = **{price} TK**")
            selected_tests.append(f"<tr><td>{test}</td><td style='text-align:right'>{price} TK</td></tr>")
            total_amount += price

    discount = st.number_input("Discount (TK)", min_value=0, value=0, step=10)
    total_paid = total_amount - discount

    st.markdown(f"**Total:** {total_amount} TK")
    st.markdown(f"**Discount:** {discount} TK")
    st.markdown(f"### **Net Payable: {total_paid} TK**")

    if st.button("Save Invoice", type="primary"):
        if patient_name and ref_dr != "Select Doctor":
            new_row = pd.DataFrame([{
                "Date": date_today, "Patient": patient_name, "Age": age,
                "Doctor": ref_dr, "Total": total_amount, "Discount": discount, "Paid": total_paid
            }])
            st.session_state['sales_data'] = pd.concat([st.session_state['sales_data'], new_row], ignore_index=True)
            st.success("✅ Bill Saved Successfully!")
        else:
            st.error("Patient Name এবং Doctor সিলেক্ট করুন")

with tab2:
    st.header("Admin Dashboard")
    df = st.session_state['sales_data']
    if not df.empty:
        daily = df['Paid'].sum()
        st.metric("Total Collection", f"৳ {daily}")
        st.dataframe(df)
    else:
        st.info("এখনো কোনো বিল তৈরি হয়নি")
