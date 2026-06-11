import streamlit as st
import pandas as pd
import sqlite3
import datetime

def show_live_sidebar():
    # আপনার রিয়েল ডাটাবেসের নাম সরাসরি ফিক্সড করে দেওয়া হলো
    db_name = "rogmukti_clinic_fix.db"
    table_name = "billing_records"
    total_cash = 0
    total_due = 0
    total_patients = 0

    try:
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(db_name) as conn:
            df_today = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE date LIKE '{today_date}%'", conn)
        
        if not df_today.empty:
            total_patients = len(df_today)
            cash_col = [c for c in df_today.columns if 'total' in c.lower() or 'amount' in c.lower() or 'paid' in c.lower() or 'net_paid' in c.lower()]
            due_col = [c for c in df_today.columns if 'due' in c.lower()]
            
            if cash_col: total_cash = df_today[cash_col[0]].sum()
            if due_col: total_due = df_today[due_col[0]].sum()
    except:
        pass

    # সাইডবার ডিজাইন
    with st.sidebar:
        st.markdown("## 🏥 Rog Mukti Diagnostic")
        st.markdown(f"📅 **তারিখ:** {datetime.datetime.now().strftime('%d %B, %Y')}")
        st.markdown("---")
        st.markdown("### 📝 আজকের লাইভ হিসাব")
        st.success(f"👥 **মোট রোগী:** {total_patients} জন")
        st.info(f"💰 **মোট কালেকশন:** {int(total_cash)} ৳")
        st.error(f"⚠️ **মোট বাকি (Due):** {int(total_due)} ৳")
        st.markdown("---")
        st.markdown("### ⚠️ ক্রিটিক্যাল ল্যাব অ্যালার্ট")
        st.error("🚨 **ID: P-2041** - Hb: 5.2")
        st.error("🚨 **ID: P-2055** - Sugar: 24.1")
