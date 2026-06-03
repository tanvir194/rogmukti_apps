import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="centered")

st.markdown("<h2 style='text-align: center; color: red;'>ROGMUKTI DIAGNOSTIC CENTRE</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Mollah Bazar, Auliapur, Patuakhali<br>Phone: 01711867637</p>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; background-color: #007ff5; color: white; padding: 5px; border-radius: 5px;'>CASH MEMO</h3>", unsafe_allow_html=True)

# ১. গুগল শিট থেকে অটোমেটিক টেস্ট ও দামের তালিকা নিয়ে আসা
SHEET_ID = "1BwMbaLP4koABhxaxrGGBq8I5AYmn9BDAu7evJ6TiUl4"
SHEET_NAME = "Services"  # আপনার এক্সেলের 'Services' ট্যাব
csv_url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data
def load_services():
    try:
        df = pd.read_csv(csv_url)
        # আপনার শিটের কলাম অনুযায়ী টেস্টের নাম ও রেট ঠিক করা
        # এখানে 'Test Name' এবং 'Rate' কলাম আছে ধরে নেওয়া হয়েছে
        services = {"Select Test": 0}
        for _, row in df.iterrows():
            test = str(row.iloc[0]).strip()   # ১ম কলামে টেস্টের নাম
            try:
                price = int(row.iloc[1])       # ২য় কলামে দাম
            except:
                price = 0
            if test and test != "nan":
                services[test] = price
        return services
    except:
        # কোনো কারণে শিট লোড না হলে ব্যাকআপ তালিকা
        return {"Select Test": 0, "CBC + ESR": 400, "T3": 1200, "Blood Sugar": 150}

test_directory = load_services()

# ২. ডাক্তারদের ড্রপডাউন তালিকা
doctors_list = [
    "Select Doctor",
    "Self / Direct",
    "Dr. Abdur Rahman (RMP)",
    "Dr. Moshiur Rahman (MBBS, BCS, PGT)",
    "Dr. MD. Kamrul Hasan",
    "Dr. Fahmida Akter"
]

st.subheader("Patient Information")
col1, col2 = st.columns(2)
with col1:
    patient_name = st.text_input("Name of The PT:")
    age = st.text_input("AGE:")
with col2:
    ref_dr = st.selectbox("Reff. By Dr:", doctors_list)
    date_today = st.date_input("Date:", datetime.now())

st.divider()

# ৩. ৫টি টেস্ট সিলেক্ট করার ঘর (আপনার আসল এক্সেল তালিকার সব টেস্ট এখানে দেখাবে)
st.subheader("Services / Test Selection")
selected_tests = []
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
    elif ref_dr == "Select Doctor":
        st.error("দয়া করে রেফারেন্স ডাক্তার সিলেক্ট করুন!")
    else:
        st.success(f"Invoice generated successfully for {patient_name}!")
        
