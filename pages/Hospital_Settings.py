import streamlit as st
import sqlite3

conn = sqlite3.connect('rogmukti.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        hospital_name TEXT,
        address TEXT,
        phone TEXT,
        email TEXT
    )
''')
conn.commit()

st.title("⚙️ হাসপাতাল সেটিংস")

# বর্তমান ডাটা লোড করা
c.execute("SELECT hospital_name, address, phone, email FROM settings WHERE id = 1")
current_settings = c.fetchone()

if current_settings:
    default_name, default_address, default_phone, default_email = current_settings
else:
    default_name, default_address, default_phone, default_email = "রোগমুক্তি হাসপাতাল", "", "", ""

# আপডেট ফর্ম
with st.form("settings_form"):
    hospital_name = st.text_input("হাসপাতালের নাম", default_name)
    address = st.text_input("ঠিকানা", default_address)
    phone = st.text_input("মোবাইল/ফোন নম্বর", default_phone)
    email = st.text_input("ইমেইল অ্যাড্রেস", default_email)
    
    save_settings = st.form_submit_button("কনফিগারেশন সেভ করুন")

if save_settings:
    c.execute("INSERT OR REPLACE INTO settings (id, hospital_name, address, phone, email) VALUES (1, ?, ?, ?, ?)",
              (hospital_name, address, phone, email))
    conn.commit()
    st.success("⚙️ হাসপাতালের প্রোফাইল সফলভাবে আপডেট করা হয়েছে!")
    st.rerun()

conn.close()
