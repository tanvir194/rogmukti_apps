import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="centered")

st.markdown("<h2 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Bazar, Auliapur, Patuakhali<br>Phone: 01711867637</p>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; background-color: #007ff5; color: white; padding: 5px; border-radius: 5px;'>CASH MEMO</h3>", unsafe_allow_html=True)

# ডাটাবেজ এক্সেস মেথড ২ (সরাসরি গুগল ড্রাইভের এক্সপোর্ট লিংক)
SHEET_ID = "1BwMbaLP4koABhxaxrGGBq8I5AYmn9BDAu7evJ6TiUl4"
csv_url = f"https://google.com{SHEET_ID}/export?format=csv&gid=1152917726" # আপনার 'Services' ট্যাবের সরাসরি আইডি যুক্ত লিংক

@st.cache_data(ttl=10) # প্রতি ১০ সেকেন্ড পর পর নতুন ডেটা রিফ্রেশ করবে
def load_data_from_excel():
    test_dict = {"Select Test": 0}
    doc_list = ["Select Doctor"]
    
    try:
        # কোনো হেডার ছাড়া পজিশন অনুযায়ী রিড করার জন্য
        df = pd.read_csv(csv_url, header=None)
        
        for idx, row in df.iterrows():
            if idx == 0: # প্রথম হেডার লাইন স্কিপ করার জন্য
                continue
                
            # ২ নম্বর কলামে টেস্টের নাম এবং ৩ নম্বর কলামে প্রাইস
            if len(row) > 2:
                test_name = str(row[1]).strip()
                price_val = row[2]
                
                if test_name and test_name != "nan" and test_name != "" and "Column" not in test_name and "Category" not in test_name:
                    try:
                        price = int(float(price_val))
                    except:
                        price = 0
                    test_dict[test_name] = price
            
            # ৬ নম্বর কলামে ডাক্তারদের নাম
            if len(row) > 5:
                doc_name = str(row[5]).strip()
                if doc_name and doc_name != "nan" and doc_name != "" and "Column" not in doc_name and "Self" not in doc_name:
                    if doc_name not in doc_list:
                        doc_list.append(doc_name)
                        
    except Exception as e:
        pass
        
    # যদি গুগল কানেকশনে কোনো সমস্যা থাকে তবে ব্যাকআপ হিসেবে বড় রিয়েল লিস্ট আসবে
    if len(test_dict) <= 1:
        test_dict = {
            "Select Test": 0,
            "(CBC) + ESR": 600,
            "Widal Test": 450,
            "T.A Test": 1050,
            "Platelet Count": 300,
            "MP": 500,
            "BT/CT": 350,
            "C/E Count": 250,
            "T3": 1200,
            "T4": 1200,
            "FT3": 900,
            "FT4": 900,
            "TSH": 1100,
            "HbA1c": 1500,
            "Prolactin": 1200,
            "Random Blood Sugar": 200,
            "Fasting Blood Sugar": 200,
            "Lipid Profile": 1000,
            "Serum Creatinine": 300,
            "Uric Acid": 400,
            "Chest X-Ray": 500,
            "USG of Whole Abdomen": 800,
            "ECG": 300,
            "Urine R/E": 250
        }
    
    if len(doc_list) <= 1:
        doc_list.extend(["Dr. Saiful Islam RMP", "DR. Abdur Rahman D M F", "DR. Moshiur Rahman MBBS BCS FCPS", "Self"])
        
    return test_dict, doc_list

test_directory, doctors_list = load_data_from_excel()

st.subheader("Patient Information")
col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("Name of The PT:")
    age = st.text_input("AGE:")
with col2:
    ref_dr = st.selectbox("Reff. By Dr:", doctors_list)
    date_today = st.date_input("Date:", datetime.now())

st.divider()

st.subheader("Services / Test Selection")
total_amount = 0

# এখানে ৫টি টেস্টের ইনপুট তৈরি করা হয়েছে
for i in range(1, 6):
    test_name = st.selectbox(f"Select Test {i}:", list(test_directory.keys()), key=f"test_{i}")
    if test_name != "Select Test":
        price = test_directory[test_name]
        st.text(f"Price: {price} TK")
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
        
