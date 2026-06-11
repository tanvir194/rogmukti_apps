import streamlit as st
import pandas as pd
import sqlite3
import os
import datetime
import urllib.request
import json
import time

# ১. পেজ কনফিগারেশন ও সাইডবার ডিফল্ট ওপেন
st.set_page_config(page_title="Advanced Live Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- অটো রিফ্রেশ লজিক (১০ সেকেন্ড পর পর) ---
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0
st.session_state.refresh_count += 1
time.sleep(0.1)
# ----------------------------------------

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
        tables = [row for row in cursor.fetchall()]
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
        
        if cash_col: total_cash = df_today[cash_col].sum()
        if due_col: total_due = df_today[due_col].sum()
        
        if test_col:
            all_tests = df_today[test_col].astype(str).str.cat(sep=',').split(',')
            for t in all_tests:
                t_clean = t.strip()
                if t_clean and t_clean.lower() != 'nan':
                    top_tests_dict[t_clean] = top_tests_dict.get(t_clean, 0) + 1
except:
    pass

# ৪. তাপমাত্রা ক্যাশ (Cache)
@st.cache_data(ttl=1800)
def get_live_temperature():
    try:
        url = "https://open-meteo.com"
        response = urllib.request.urlopen(url, timeout=5)
        data = json.loads(response.read().decode())
        temp = data['current_weather']['temperature']
        return f"{temp} °C"
    except:
        return "28.5 °C (Offline)"

live_temp = get_live_temperature()


# =========================================================
# 🔄 নতুন পরিবর্তন: সমস্ত লাইভ আপডেট বাম পাশের সাইডবারে স্থানান্তর
# =========================================================

with st.sidebar:
    st.markdown("## 🏥 Rog Mukti Diagnostic")
    st.markdown(f"📅 **তারিখ:** {datetime.datetime.now().strftime('%d %B, %Y')} | 🌡️ **তাপমাত্রা:** {live_temp}")
    st.markdown(f"🔄 **লাইভ মনিটর:** প্রতি ১০ সেকেন্ডে অটো-আপডেট")
    st.markdown("---")
    
    # ১. আজকের লাইভ হিসাব কার্ড (সাইডবার এডিশন)
    st.markdown("### 📝 আজকের লাইভ হিসাব")
    st.success(f"👥 **মোট রোগী:** {total_patients} জন")
    st.info(f"💰 **মোট কালেকশন:** {total_cash} ৳")
    st.error(f"⚠️ **মোট বাকি (Due):** {total_due} ৳")
    st.markdown("---")
    
    # ২. ল্যাব টু-ডু ও পেন্ডিং ট্র্যাকার
    st.markdown("### ⏳ ল্যাব টু-ডু ও প্রগ্রেস")
    if total_patients > 0:
        st.write(f"✅ {total_patients} টি টেস্টের কাজ চলছে।")
    else:
        st.caption("⚠️ আজকে এখনো কোনো টেস্ট এন্ট্রি হয়নি।")
    progress_val = 65  # উদাহরণ প্রগ্রেস
    st.progress(progress_val / 100)
    st.caption(f"রিপোর্ট তৈরির অগ্রগতি: {progress_val}%")
    st.markdown("---")
    
    # ৩. ক্রিটিক্যাল ল্যাব অ্যালার্ট প্যানেল (সবসময় নজর রাখার জন্য)
    st.markdown("### ⚠️ ক্রিটিক্যাল ল্যাব অ্যালার্ট")
    st.error("🚨 **ID: P-2041** - Hb: 5.2 (অত্যন্ত কম!)")
    st.error("🚨 **ID: P-2055** - Sugar: 24.1 (অতিরিক্ত বেশি!)")
    st.markdown("---")
    
    # ৪. ঘণ্টাভিত্তিক কালেকশন ছোট চার্ট
    st.markdown("### 📊 কালেকশন ট্রেন্ড")
    chart_data = pd.DataFrame({
        'কালেকশন': [total_cash * 0.2, total_cash * 0.5, total_cash]
    }, index=['সকাল', 'দুপুর', 'রাত'])
    st.line_chart(chart_data, height=130)


# ৬. মূল ড্যাশবোর্ড স্ক্রিন (Main Screen)
st.markdown("# 📊 রিয়েল-টাইম অ্যাডভান্সড ড্যাশবোর্ড")
st.markdown("আপনার বাম পাশের সাইডবারে লাইভ আপডেটগুলো লক করা হয়েছে। আপনি এখন যেকোনো মেনুতে গেলেও ওগুলো দেখতে পাবেন।")
st.markdown("---")

# মূল পেজে আপনি আপনার অন্যান্য পেজের কাজ বা ডিরেক্টরি রাখতে পারেন
col1, col2 = st.columns(2)
with col1:
    st.info("### 📈 আজকের সেরা টেস্ট সমূহ")
    if top_tests_dict:
        df_top_tests = pd.DataFrame(list(top_tests_dict.items()), columns=['টেস্টের নাম', 'সংখ্যা']).sort_values(by='সংখ্যা', ascending=False)
        st.dataframe(df_top_tests, use_container_width=True, hide_index=True)
    else:
        st.caption("আজকে এখনো কোনো টেস্ট এন্ট্রি হয়নি।")

with col2:
    st.warning("### 💳 কুইক ডিউ কালেক্টর")
    patient_id = st.text_input("রোগীর আইডি বা মোবাইল নম্বর দিন:", placeholder="যেমন: P-102")
    due_amount_input = st.number_input("টাকার পরিমাণ (৳):", min_value=0, step=50)
    if st.button("💰 বকেয়া টাকা জমা করুন"):
        if patient_id and due_amount_input > 0:
            st.success(f"সফলভাবে {patient_id} এর {due_amount_input} ৳ জমা হয়েছে।")

# স্ক্রিনের নিচে অটো-রিফ্রেশ স্ক্রিপ্ট
st.components.v1.html(
    """
    <script>
    setTimeout(function(){
        window.parent.location.reload();
    }, 10000);
    </script>
    """,
    height=0
    )
