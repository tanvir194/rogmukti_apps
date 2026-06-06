import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
from fpdf import FPDF
import billing_logic

st.set_page_config(page_title="Rogmukti Diagnostic Centre", page_icon="🏥", layout="wide")

def make_hashes(password): 
    return hashlib.sha256(str.encode(password)).hexdigest()

if 'logged_in' not in st.session_state: 
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state: 
    st.session_state['user_role'] = None

if not st.session_state['logged_in']:
    st.subheader("🔑 Login to Rogmukti Panel")
    username = st.text_input("User Name")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = "Admin"
            st.rerun()
        elif username == "labtech" and password == "lab123":
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = "Lab Technician"
            st.rerun()
        else: 
            st.error("Invalid Username or Password")
    st.stop()

conn = sqlite3.connect('rogmukti.db', check_same_thread=False)
c = conn.cursor()

st.sidebar.title("🏥 Rogmukti Menu")
page = st.sidebar.radio("Go to Page:", ["📊 Dashboard & Reports", "💳 New Patient Billing"])
if st.sidebar.button("Log Out"):
    st.session_state['logged_in'] = False
    st.rerun()

if page == "📊 Dashboard & Reports":
    billing_logic.render_dashboard(st, conn, c)
elif page == "💳 New Patient Billing":
    billing_logic.render_billing(st, conn, c, FPDF, datetime)
  
