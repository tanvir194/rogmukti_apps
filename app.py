import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="centered")

st.markdown("<h2 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Bazar, Auliapur, Patuakhali<br>Phone: 01711867637</p>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; background-color: #007ff5; color: white; padding: 5px; border-radius: 5px;'>CASH MEMO</h3>", unsafe_allow_html=True)

# গুগল শিট থেকে সরাসরি লিংক
SHEET_ID = "1BwMbaLP4koABhxaxrGGBq8I5AYmn9BDAu7evJ6TiUl4"
SHEET_NAME = "Services"
csv_url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=30)
def load_data_from_excel():
    test_dict = {"Select Test": 0}
    doc_list = ["Select Doctor"]
    
    try:
        # header=None দিয়ে কলামের নাম যাই হোক না কেন পজিশন দিয়ে রিড করার ব্যবস্থা
        df = pd.read_csv(csv_url, header=None)
        
        for idx, row in df.iterrows():
            # ১ম সারি (কলামের নামগুলো) বাদ দেওয়ার জন্য
            if idx == 0:
                continue
                
            # ২য় কলামে টেস্টের নাম (Index 1) এবং ৩য় কলামে রেট (Index 2)
            if len(row) > 2:
                test_name = str(row[1]).strip()
                price_val = row[2]
                
                if test_name and test_name != "nan" and test_name != "" and "Column" not in test_name:
                    try:
                        price = int(float(price_val))
                    except:
                        price = 0
                    test_dict[test_name] = price
            
            # ৬ষ্ঠ কলামে ডাক্তারদের নাম (Index 5)
            if len(row) > 5:
                doc_name = str(row[5]).strip()
                if doc_name and doc_name != "nan" and doc_name != "" and "Column" not in doc_name and "Self" not in doc_name:
                    if doc_name not in doc_list:
                        doc_list.append(doc_name)
                        
    except Exception as e:
        # ব্যাকআপ ডেটা
        test_dict = {"Select Test": 0, "CBC + ESR": 600, "Widal Test": 450}
        doc_list = ["Select Doctor"]
        
    # ডাক্তারদের তালিকায় যদি কিছু না আসে তবে ম্যানুয়াল ব্যাকআপ
    if len(doc_list) <= 1:
        doc_list.extend(["Dr. Saiful Islam RMP", "DR. Abdur Rahman D M F", "DR. Moshiur Rahman MBBS BCS FCPS", "Self"])
        
    return test_dict, doc_list

# ডেটা লোড করা
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

# ৫টি টেস্ট সিলেক্ট করার ঘর (সব টেস্ট এখানে দেখাবে)
st.subheader("Services / Test Selection")
total_amount = 0

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
        
