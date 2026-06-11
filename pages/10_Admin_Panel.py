import streamlit as st
import pandas as pd
import sqlite3
import os

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Admin Master Control", layout="wide")

st.title("🛠️ Rog Mukti All-in-One Master Control Panel")
st.write("এই একটি পেজ থেকেই আপনার পুরো অ্যাপের ডাটাবেজ এবং টেস্টের রেট কন্ট্রোল হবে।")
st.markdown("---")

# ২. সঠিক ডাটাবেজ ফাইল অটো-ডিটেক্ট করা
db_name = "database.db"
for file in os.listdir('.'):
    if file.endswith('.db'):
        db_name = file

# ৩. ডাটাবেজ টেবিল চেক ও তৈরি করা
def init_db():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # টেস্টের প্রাইস লিস্ট টেবিল (যদি না থাকে)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_prices (
            test_name TEXT PRIMARY KEY,
            price REAL
        )
    ''')
    # শুরুতে কিছু ডিফল্ট টেস্ট যোগ করা (যদি টেবিল খালি থাকে)
    cursor.execute("SELECT COUNT(*) FROM test_prices")
    if cursor.fetchone() == 0:
        default_tests = [("CBC", 400), ("Lipid Profile", 1000), ("Blood Sugar", 150), ("Urine RE", 250)]
        cursor.executemany("INSERT INTO test_prices VALUES (?, ?)", default_tests)
    conn.commit()
    conn.close()

init_db()

# ৪. মেইন ইন্টারফেস (২টি কলাম)
col1, col2 = st.columns(2, gap="large")

with col1:
    st.header("🧪 নতুন টেস্ট যোগ ও মূল্য পরিবর্তন")
    st.info("এখানে টেস্টের দাম পরিবর্তন করলে তা পুরো অ্যাপের সব পেজে আপডেট হয়ে যাবে।")
    
    with st.form("test_edit_form", clear_on_submit=True):
        t_name = st.text_input("টেস্টের নাম লিখুন (সঠিক বানান দিন):")
        t_price = st.number_input("টেস্টের মূল্য (BDT):", min_value=0.0, step=10.0)
        submit_btn = st.form_submit_button("অ্যাপের ডাটাবেজে আপডেট করুন")
        
        if submit_btn and t_name:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO test_prices (test_name, price) VALUES (?, ?)", (t_name, t_price))
            conn.commit()
            conn.close()
            st.success(f"🎉 '{t_name}' টেস্টের মূল্য {t_price} BDT হিসেবে লাইভ অ্যাপে সেট হয়েছে!")
            st.rerun()

with col2:
    st.header("📋 লাইভ ডাটাবেজ রেট চার্ট")
    # ডাটাবেজ থেকে রিড করে téবিলে দেখানো
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query("SELECT test_name AS 'টেস্টের নাম', price AS 'মূল্য (BDT)' FROM test_prices", conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True, height=300)

st.markdown("---")
st.header("🗑️ টেস্ট ডিলিট করার প্যানেল")
# টেস্ট ডিলিট করার ফর্ম
with st.form("delete_form"):
    delete_name = st.selectbox("অ্যাপ থেকে যে টেস্টটি মুছে ফেলতে চান সেটি সিলেক্ট করুন:", [""] + list(df['টেস্টের নাম']))
    delete_btn = st.form_submit_button("🔴 টেস্টটি চিরতরে মুছে ফেলুন")
    
    if delete_btn and delete_name:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM test_prices WHERE test_name = ?", (delete_name,))
        conn.commit()
        conn.close()
        st.error(f"🗑️ '{delete_name}' টেস্টটি অ্যাপ থেকে সফলভাবে মুছে ফেলা হয়েছে।")
        st.rerun()
