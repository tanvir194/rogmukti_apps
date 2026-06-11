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
        tables = [row for row in cursor.fetchall()]
        for t in tables:
            if 'bill' in t[0].lower() or 'patient' in t[0].lower() or 'record' in t[0].lower():
                table_name = t[0]
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

# ৪. তাপমাত্রা ক্যাশ (Cache) করা হলো যাতে অ্যাপ স্লো না হয়
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

# ৫. সাইডবার ডিজাইন
st.sidebar.markdown("## Rog Mukti Diagnostic")
st.sidebar.markdown(f"📅 **তারিখ:** {datetime.datetime.now().strftime('%d %B, %Y')}")
st.sidebar.markdown(f"🌡️ **আজকের তাপমাত্রা:** {live_temp}")
st.sidebar.markdown("---")

try:
    st.sidebar.markdown("### 📝 আজকের লাইভ হিসাব")
    st.sidebar.markdown(f"• **মোট রোগী:** {total_patients} জন")
    st.sidebar.markdown(f"• **মোট কালেকশন:** {total_cash} ৳")
    st.sidebar.markdown(f"• **মোট বাকি (Due):** {total_due} ৳")
except:
    pass

# ৬. মূল ড্যাশবোর্ড হেডার ডিজাইন
st.markdown("# 📊 রিয়েল-টাইম অ্যাডভান্সড ড্যাশবোর্ড ও ল্যাব মনিটর")
st.markdown("এই পেজটি আপনার ডায়াগনস্টিক সেন্টারের লাইভ প্যাথলজি অপারেশন এবং আজকের কাজের অগ্রগতি ট্র্যাক করছে।")
st.markdown("---")

# ৭. গ্রিড লেআউট তৈরি (বাম এবং ডান কলাম)
col1, col2 = st.columns(2)

with col1:
    # ল্যাব টু-ডু ও পেন্ডিং টেস্ট ট্র্যাকার কার্ড
    st.info("### 📝 ল্যাব টু-ডু ও পেন্ডিং টেস্ট ট্র্যাকার")
    st.write("আজকে কাউন্টারে এন্ট্রি হওয়া রিসিট সমূহের লাইভ অবস্থা।")
    
    # এখানে আপনার পেন্ডিং টেস্টের ডেটা দেখানোর কোড বসবে
    # সাময়িকভাবে একটি ডামি মেসেজ বা প্রগ্রেস বার দেওয়া হলো
    if total_patients > 0:
        st.success(f"আজকের মোট {total_patients} টি টেস্টের কাজ প্রক্রিয়াধীন রয়েছে।")
    else:
        st.warning("আজকে এখনো কোনো টেস্ট কাউন্টারে এন্ট্রি হয়নি।")

with col2:
    # ইমার্জেন্সি রিয়্যাক্ট ও নোটিফিকেশন কার্ড
    st.error("### 🚨 ইমার্জেন্সি রিয়্যাক্ট ও নোটিফিকেশন")
    st.write("জরুরি বার্তার বিষয়:")
    emergency_msg = st.text_input("এখানে টাইপ করুন...", placeholder="জরুরি কোনো নোটিশ থাকলে লিখুন")
    if st.button("🚨 লাইভ জরুরি এলার্ট জারি করুন"):
        if emergency_msg:
            st.toast(f"এলার্ট জারি হয়েছে: {emergency_msg}")
        else:
            st.toast("অনুগ্রহ করে আগে বার্তাটি লিখুন।")
            
    st.markdown("---")
    
    # কুইক ল্যাব ডিরেক্টরি কার্ড
    st.success("### 📞 কুইক ল্যাব ডিরেক্টরি")
    with st.expander("📞 জরুরি ফোন নম্বর সমূহ দেখতে এখানে ক্লিক করুন"):
        st.write("• প্যাথলজি ল্যাব ইন-চার্জ: +৮৮০১XXXXXXXXX")
        st.write("• রিলিজ ডেস্ক: +৮৮০১XXXXXXXXX")
        st.write("• আইটি সাপোর্ট টিম: +৮৮০১XXXXXXXXX")
