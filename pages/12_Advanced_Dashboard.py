import streamlit as st
import pandas as pd
import sqlite3
import os
import datetime
import urllib.request
import json

# ১. পেজ কনফিগারেশন ও সাইডবার ডিফল্ট ওপেন
st.set_page_config(page_title="Advanced Live Dashboard", layout="wide", initial_sidebar_state="expanded")

# ২. ডেটাবেস ফাইল অটো-ডিটেক্ট
db_name = "database.db"
for file in os.listdir('.'):
    if file.endswith('.db'):
        db_name = file

table_name = "billing_records"
try:
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        for t in tables:
            if 'bill' in t.lower() or 'patient' in t.lower() or 'record' in t.lower():
                table_name = t
                break
except:
    pass

# ৩. ডাটাবেস থেকে আজকের লাইভ ডাটা ঠিক করা
today_date = datetime.datetime.now().strftime("%Y-%m-%d")
total_cash = 0
total_due = 0
total_patients = 0
top_tests_dict = {}

try:
    with sqlite3.connect(db_name) as conn:
        df_today = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE date LIKE '{today_date}%'", conn)
    
    if not df_today.empty:
        total_patients = len(df_today)
        
        cash_col = [c for c in df_today.columns if 'total' in c.lower() or 'amount' in c.lower() or 'paid' in c.lower()]
        due_col = [c for c in df_today.columns if 'due' in c.lower()]
        test_col = [c for c in df_today.columns if 'test' in c.lower()]
        
        if cash_col: total_cash = df_today[cash_col[0]].sum()
        if due_col: total_due = df_today[due_col[0]].sum()
        
        if test_col:
            all_tests = df_today[test_col[0]].str.cat(sep=',').split(',')
            for t in all_tests:
                if t.strip():
                    top_tests_dict[t.strip()] = top_tests_dict.get(t.strip(), 0) + 1
except:
    pass

# ৪. এপিআই স্লো হওয়ার কারণে অ্যাপ যেন আটকে না যায়, তাই তাপমাত্রা ক্যাশ (Cache) করা হলো
@st.cache_data(ttl=1800) # একবার লোড হলে ৩০ মিনিট পর্যন্ত এই ডেটা মেমোরিতে থাকবে, অ্যাপ স্লো হবে না
def get_live_temperature():
    try:
        # সঠিক ওপেন-মেটিও এপিআই ইউআরএল
        url = "https://open-meteo.com"
        response = urllib.request.urlopen(url, timeout=5) # টাইমআউট ৫ সেকেন্ড করা হলো
        data = json.loads(response.read().decode())
        temp = data['current_weather']['temperature']
        return f"{temp} °C"
    except:
        return "28.5 °C (Offline)"

live_temp = get_live_temperature()

# ৫. সাইডবার ডিজাইন (আপনার আগের কোড অনুযায়ী)
st.sidebar.markdown("## Rog Mukti Diagnostic")
st.sidebar.markdown(f"📅 **তারিখ:** {datetime.datetime.now().strftime('%d %B, %Y')}")
st.sidebar.markdown(f"🌡️ **আজকের তাপমাত্রা:** {live_temp}")
st.sidebar.markdown("---")

# ৬. কাউন্টার ১: Today's Quick Summary
try:
    st.sidebar.markdown("### 📝 আজকের লাইভ হিসাব")
    st.sidebar.markdown(f"• **মোট রোগী:** {total_patients} জন")
    st.sidebar.markdown(f"• **মোট কালেকশন:** {total_cash} ৳")
    st.sidebar.markdown(f"• **মোট বাকি (Due):** {total_due} ৳")
except:
    pass
