import streamlit as st
import pandas as pd
import sqlite3
import os

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Admin Super Control", layout="wide")

# ২. লগইন ট্র্যাকিং সেশন তৈরি
if 'admin_panel_logged_in' not in st.session_state:
    st.session_state.admin_panel_logged_in = False

st.title("🎛️ Rog Mukti App Super Control Center")
st.markdown("---")

# ৩. পাসওয়ার্ড প্রটেকশন লজিক
if not st.session_state.admin_panel_logged_in:
    st.subheader("🔒 এই পেজটি পাসওয়ার্ড দ্বারা সুরক্ষিত")
    st.write("মাস্টার কন্ট্রোল প্যানেলে প্রবেশ করতে নিচে সঠিক পাসওয়ার্ড দিন:")
    
    # পাসওয়ার্ড ইনপুট বক্স
    input_password = st.text_input("পাসওয়ার্ড লিখুন:", type="password", key="panel_pass_input")
    
    if st.button("কন্ট্রোল প্যানেল আনলক করুন"):
        if input_password == "tanvir": # আপনার দেওয়া পাসওয়ার্ড tanvir সেট করা হলো
            st.session_state.admin_panel_logged_in = True
            st.success("🔓 সফলভাবে আনলক হয়েছে! পেজটি রিফ্রেশ হচ্ছে...")
            st.rerun()
        else:
            st.error("❌ ভুল পাসওয়ার্ড! সঠিক পাসওয়ার্ড দিয়ে আবার চেষ্টা করুন।")
            
    st.stop() # পাসওয়ার্ড না দেওয়া পর্যন্ত নিচের কোনো কোড বা ট্যাব রান হবে না

# ================= লগইন সফল হলে নিচের মাস্টার কোডটি রান হবে =================

st.success("🔓 আপনি বর্তমানে মাস্টার অ্যাডমিন হিসেবে লগইন আছেন।")
if st.button("🔴 প্যানেলটি পুনরায় লক করুন (Logout)"):
    st.session_state.admin_panel_logged_in = False
    st.rerun()

st.markdown("---")

# ৪. ডাটাবেজ ফাইল অটো-ডিটেক্ট করা
db_name = "database.db"
for file in os.listdir('.'):
    if file.endswith('.db'):
        db_name = file

# ৫. ট্যাব ভিত্তিক অল-ইন-ওয়ান মাস্টার মেনু তৈরি
tab1, tab2, tab3 = st.tabs(["🧪 টেস্ট ও রেট চার্ট কন্ট্রোল", "🗑️ রিসিট ডিলিট প্যানেল", "💰 ডিউ ও অন্যান্য ডাটা কন্ট্রোল"])

# ================= TAB 1: টেস্ট ও রেট চার্ট কন্ট্রোল =================
with tab1:
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("📝 নতুন টেস্ট যোগ ও মূল্য পরিবর্তন")
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
        st.subheader("📋 লাইভ রেট চার্ট")
        conn = sqlite3.connect(db_name)
        try:
            df_tests = pd.read_sql_query("SELECT test_name AS 'টেস্টের নাম', price AS 'মূল্য (BDT)' FROM test_prices", conn)
        except:
            df_tests = pd.DataFrame(columns=['টেস্টের নাম', 'মূল্য (BDT)'])
        conn.close()
        st.dataframe(df_tests, use_container_width=True, height=220)

    st.markdown("---")
    st.subheader("🗑️ টেস্ট মুছে ফেলার প্যানেল")
    with st.form("delete_test_form"):
        delete_t_name = st.selectbox("অ্যাপ থেকে যে টেস্টটি মুছে ফেলতে চান সেটি সিলেক্ট করুন:", [""] + list(df_tests['টেস্টের নাম']))
        delete_t_btn = st.form_submit_button("🔴 টেস্টটি চিরতরে মুছে ফেলুন")
        
        if delete_t_btn and delete_t_name:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM test_prices WHERE test_name = ?", (delete_t_name,))
            conn.commit()
            conn.close()
            st.error(f"🗑️ '{delete_t_name}' টেস্টটি অ্যাপ থেকে সফলভাবে মুছে ফেলা হয়েছে।")
            st.rerun()
            
