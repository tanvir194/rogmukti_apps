import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="centered")

# ====================== ডাটাবেস সেটআপ ======================
conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS bills
             (invoice_no TEXT, date TEXT, patient TEXT, age TEXT, phone TEXT, 
              doctor TEXT, total REAL, discount REAL, paid REAL)''')
conn.commit()

# ইউজার লগইন সিস্টেম (আপনি পরে আরও ইউজার যোগ করতে পারবেন)
users = {
    "reception": {"password": "1234", "role": "Receptionist"},
    "doctor": {"password": "1234", "role": "Doctor"},
    "admin": {"password": "admin123", "role": "Admin"}
}

# ====================== লগইন পেজ ======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

if not st.session_state.logged_in:
    st.title("🔐 Rogmukti Diagnostic Centre - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = users[username]["role"]
            st.session_state.username = username
            st.success(f"Welcome {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()

# ====================== মেইন অ্যাপ ======================
st.sidebar.success(f"Logged in as: {st.session_state.username} ({st.session_state.role})")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.title("ROGMUKTI DIAGNOSTIC CENTRE")

# বাকি কোড (বিলিং + ড্যাশবোর্ড) এখানে যোগ করব পরে

st.info("লগইন সিস্টেম সফলভাবে যোগ করা হয়েছে।")
st.caption("Developed for Rogmukti Diagnostic Centre")
