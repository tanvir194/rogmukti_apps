import streamlit as st
import sqlite3
import sys
from datetime import datetime

sys.path.append(".")
from sidebar_monitor import show_live_sidebar
show_live_sidebar()

# ০. সিকিউরিটি চেক (নিরাপত্তা ব্যবস্থা)
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("আক্রমণ চিহ্নিতকরণ! দয়া করে হোম পেজ থেকে লগইন করুন।")
    st.stop()

# ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

st.title("📝 টেস্ট এবং বিলিং সেকশন")

# ১. পেশেন্ট ইনফরমেশন সেকশন
st.subheader("পেশেন্ট ইনফরমেশন")
col_n1, col_n2 = st.columns(2)
with col_n1:
    name = st.text_input("পেশেন্টের নাম (Name of the PT) *")
    phone = st.text_input("মোবাইল নম্বর (Phone)")
with col_n2:
    age = st.number_input("বয়স (Age)", min_value=0, max_value=120, value=25)
    
    # ডাটাবেজ থেকে ডাক্তারদের তালিকা আনা
    c.execute("SELECT doc_name FROM doctors_list")
    db_doctors = [row[0] for row in c.fetchall()]
    doctor_options = ["Choose option"] + db_doctors + ["অন্যান্য"]
    
    selected_doctor_setup = st.selectbox("ডাক্তার সিলেক্ট করুন (Refd By):", doctor_options)

doctor = ""
if selected_doctor_setup == "অন্যান্য":
    doctor = st.text_input("✍️ নতুন ডাক্তারের নাম ও ডিগ্রি এখানে লিখুন: *")
else:
    doctor = selected_doctor_setup

st.markdown("---")

# ২. টেস্ট সিলেকশন সেকশন
st.subheader("টেস্ট সিলেকশন ও লাইভ রেট এন্ট্রি")

# ডাটাবেজ থেকে টেস্টের তালিকা আনা
try:
    c.execute("SELECT test_name FROM available_tests_list")
    available_tests = [row[0] for row in c.fetchall()]
except:
    available_tests = ["CBC", "RBS", "Serum Creatinine", "Lipid Profile", "Urine RE", "USG of W/A"]

selected_tests = st.multiselect("তালিকা থেকে টেস্ট সিলেক্ট করুন:", available_tests)

test_with_prices = []
total_fee = 0

if selected_tests:
    st.markdown("##### 📌 নির্বাচিত টেস্টগুলোর দাম এখানে লিখে দিন:")
    for test in selected_tests:
        price = st.number_input(f"ফি দিন -> {test} (টাকা):", min_value=0, value=0, step=50, key=f"price_{test}")
        total_fee += int(price)
        test_with_prices.append(f"{test}:{int(price)}")

# Custom test option (enter a new test name outside the list)
st.markdown("---")
st.markdown("##### ➕ তালিকা বহির্ভূত কাস্টম টেস্ট (ঐচ্ছিক)")
col_c1, col_c2 = st.columns(2)
with col_c1:
    custom_name = st.text_input("কাস্টম টেস্টের নাম:")
with col_c2:
    custom_price = st.number_input("কাস্টম টেস্টের দাম:", min_value=0, value=0, step=50)

if custom_name.strip():
    total_fee += int(custom_price)
    test_with_prices.append(f"{custom_name.strip()}:{int(custom_price)}")

# 📊 লাইভ মোট বিল - মডার্ন নীল কার্ড ডিজাইন (দশমিক ছাড়া)
st.markdown(
    f"""
    <div style="background-color: #e8f4f8; padding: 15px; border-left: 5px solid #29b6f6; border-radius: 5px; margin-top: 15px; margin-bottom: 15px;">
        <span style="font-size: 15px; color: #01579b; font-weight: bold;">📋 লাইভ মোট বিল (টোটাল ফি):</span><br>
        <span style="font-size: 26px; color: #01579b; font-weight: bold;">{int(total_fee)} ৳</span>
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown("---")

# ৩. পেমেন্ট ও ডিসকাউন্ট সেকশন
st.subheader("💳 পেমেন্ট ও ডিসকাউন্ট")
col3, col4 = st.columns(2)
with col3:
    discount_amount = st.number_input("ডিসকাউন্ট (টাকা)", min_value=0, value=0, step=10)
    advance_paid = st.number_input("অগ্রিম পরিশোধ (Advance Paid)", min_value=0, value=0)

net_payable = total_fee - int(discount_amount)
due_amount = net_payable - int(advance_paid)

# 🎨 ডিসকাউন্ট ও বাকি টাকা - সুন্দর ব্যানার ডিজাইন (দশমিক ছাড়া)
with col4:
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True) 
    st.success(f"💰 **ডিসকাউন্ট প্রদত্ত:** {int(discount_amount)} ৳")
    
    if due_amount > 0:
        st.error(f"⚠️ **মোট বাকি টাকা (Due):** {int(due_amount)} ৳")
    else:
        st.info(f"✅ **কোনো বাকি নেই (Paid):** {int(due_amount)} ৳")

st.markdown("---")
submit_button = st.button("Save Bill and Go to Print (বিল সেভ করুন)")

if submit_button:
    if not name or not test_with_prices:
        st.error("⚠️ পেশেন্টের নাম এবং অন্তত একটি টেস্টের নাম দেওয়া বাধ্যতামূলক!")
    elif selected_doctor_setup == "অন্যান্য" and not doctor.strip():
        st.error("⚠️ দয়া করে নতুন ডাক্তারের নাম বা ডিগ্রি এখানে লিখুন!")
    else:
        current_date = datetime.now().strftime("%Y-%m-%d")
        tests_data_str = "|".join(test_with_prices)
        
        # 🩺 ক্যাটাগরি লজিক ১: নতুন ডাক্তার অটো-সেভ
        if selected_doctor_setup == "অন্যান্য" and doctor.strip():
            try:
                c.execute("INSERT OR IGNORE INTO doctors_list (doc_name) VALUES (?)", (doctor.strip(),))
                conn.commit()
            except:
                pass
                
        # 🩺 ক্যাটাগরি লজিক ২: নতুন কাস্টম টেস্ট অটো-সেভ
        if custom_name.strip():
            try:
                c.execute("INSERT OR IGNORE INTO custom_tests_list (test_name) VALUES (?)", (custom_name.strip(),))
                conn.commit()
            except:
                pass
                
        # 🛠️ স্বয়ংক্রিয় কলাম ডিটেকশন ও ডাটা সেভিং বুলেটপ্রুফ লজিক
        try:
            c.execute("PRAGMA table_info(billing_records)")
            columns_info = c.fetchall()
            
            # প্রাইমারি কি (ID কলাম) বাদে বাকি কলামগুলোর নাম বের করা
            db_columns = [col[1] for col in columns_info if col[5] == 0]
            
            # ইনসার্ট করার জন্য প্রস্তুত করা ১০টি ভ্যালু
            all_values = [
                name, age, phone, 
                doctor.strip() if hasattr(doctor, 'strip') else doctor, 
                tests_data_str, int(total_fee), int(discount_amount), 
                int(advance_paid), int(due_amount), current_date
            ]
            
            # ডাটাবেজের কলাম সংখ্যার সাথে ম্যাচ করিয়ে ডাটা অ্যাডজাস্ট করা
            insert_values = all_values[:len(db_columns)]
            col_names = ", ".join(db_columns[:len(insert_values)])
            placeholders = ", ".join(["?"] * len(insert_values))
            
            sql_query = f"INSERT INTO billing_records ({col_names}) VALUES ({placeholders})"
            c.execute(sql_query, insert_values)
            conn.commit()
            
            st.session_state.last_invoice_id = c.lastrowid
            st.success("🎉 সফলভাবে ডাটা সেভ হয়েছে! প্রিন্ট পেজে নিয়ে যাওয়া হচ্ছে...")
            st.switch_page("pages/3_Print_Receipt.py")
            
        except Exception as db_err:
            st.error(f"❌ ডাটাবেজ সেভ করতে সমস্যা হয়েছে: {db_err}")

conn.close()
