import sys
import os
import streamlit as st
import sqlite3

# আগের সিস্টেম ঠিক রাখা (কোনো কোড না পাল্টিয়ে)
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from sidebar_monitor import show_live_sidebar

show_live_sidebar()

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ অননুমোদিত প্রবেশাধিকার! দয়া করে ড্যাশবোর্ড থেকে লগইন করুন।")
    st.stop()

st.title("⚙️ হাসপাতাল সেটিংস")

conn = sqlite3.connect('rogmukti_clinic_fix.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS hospital_settings (
        id INTEGER PRIMARY KEY,
        hospital_name TEXT,
        address TEXT,
        phone TEXT
    )
''')
conn.commit()

with st.form("settings_form"):
    h_name = st.text_input("হাসপাতালের নাম", "রোগমুক্তি ডায়াগনস্টিক")
    h_address = st.text_input("ঠিকানা")
    h_phone = st.text_input("মোবাইল নম্বর")
    save = st.form_submit_button("কনফিগারেশন সেভ করুন")

if save:
    c.execute("INSERT OR REPLACE INTO hospital_settings (id, hospital_name, address, phone) VALUES (1, ?, ?, ?)",
              (h_name, h_address, h_phone))
    conn.commit()
    st.success("⚙️ সেটিংস সফলভাবে আপডেট করা হয়েছে!")

conn.close()
