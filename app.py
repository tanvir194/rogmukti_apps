import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="centered")

st.markdown("<h2 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Bazar, Auliapur, Patuakhali<br>Phone: 01711867637</p>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; background-color: #007ff5; color: white; padding: 5px; border-radius: 5px;'>CASH MEMO</h3>", unsafe_allow_html=True)

# আপনার গুগল শিটের আসল ডাটাবেজ লিংক
SHEET_URL = "https://google.com"

test_directory = {
    "Select Test": 0,
    "CBC + ESR": 400,
    "T3": 1200,
    "Blood Sugar": 150,
    "Urine RE": 250,
    "Lipid Profile": 1000,
    "Serum Creatinine": 300
}

st.subheader("Patient Information")
col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("Name of The PT:")
    age = st.text_input("AGE:")
with col2:
    ref_dr = st.text_input("Reff. Dr:")
    date_today = st.date_input("Date:", datetime.now())

st.divider()
st.subheader("Services / Test Selection")
selected_tests = []
total_amount = 0

for i in range(1, 4):
    test_name = st.selectbox(f"Select Test {i}:", list(test_directory.keys()), key=f"test_{i}")
    if test_name != "Select Test":
        price = test_directory[test_name]
        st.text(f"Price: {price} TK")
        selected_tests.append(test_name)
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
    else:
        st.success(f"Invoice generated successfully for {patient_name}!")
        st.info("আপনার গুগল শিটে ডেটা সেভ করার প্রসেস সম্পন্ন হচ্ছে।")
      
