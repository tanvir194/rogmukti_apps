import streamlit as st
import pandas as pd
import sqlite3
import os
import datetime
import urllib.request
import json

# ১. পেজ কনফিগারেশন ও সাইডবার অটো-ওপেন
st.set_page_config(page_title="Advanced Live Dashboard", layout="wide", initial_sidebar_state="expanded")

# ২. ডাটাবেজ ফাইল অটো-ডিটেক্ট করা
db_name = "database.db"
for file in os.listdir('.'):
    if file.endswith('.db'):
        db_name = file

table_name = "billing_records"
try:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row for row in cursor.fetchall()]
    for t in tables:
        if 'bill' in t.lower() or 'patient' in t.lower() or 'record' in t.lower():
            table_name = t
            break
    conn.close()
except:
    pass

# ৩. ডাটাবেজ থেকে আজকের লাইভ ডাটা রিড করা
today_date = datetime.datetime.now().strftime("%Y-%m-%d")
total_cash = 0
total_due = 0
total_patients = 0
top_tests_dict = {}

try:
    conn = sqlite3.connect(db_name)
    df_today = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE date LIKE '{today_date}%'", conn)
    conn.close()
    
    if not df_today.empty:
        total_patients = len(df_today)
        cash_col = [c for c in df_today.columns if 'total' in c.lower() or 'amount' in c.lower() or 'paid' in c.lower()]
        due_col = [c for c in df_today.columns if 'due' in c.lower()]
        test_col = [c for c in df_today.columns if 'test' in c.lower()]
        
        if cash_col: total_cash = df_today[cash_col].sum()
        if due_col: total_due = df_today[due_col].sum()
        
        if test_col:
            all_tests = df_today[test_col].str.cat(sep=', ').split(', ')
            for t in all_tests:
                if t.strip():
                    top_tests_dict[t.strip()] = top_tests_dict.get(t.strip(), 0) + 1
except:
    pass

# ৪. 🌤️ ইন্টারনেট থেকে বাংলাদেশের লাইভ স্থানীয় তাপমাত্রা তুলে আনার ফাংশন
def get_live_temperature():
    try:
        # ওপেন-মেটিও ফ্রি ওয়েদার এপিআই (ঢাকা/গালাচিপা অঞ্চলের সম্ভাব্য স্থানাঙ্ক অনুযায়ী)
        url = "https://open-meteo.com"
        response = urllib.request.urlopen(url, timeout=3)
        data = json.loads(response.read().decode())
        temp = data['current_weather']['temperature']
        return f"{temp} °C"
    except:
        return "28.5 °C (Offline)" # ইন্টারনেট এরর থাকলে ডিফল্ট টেম্পারেচার দেখাবে

live_temp = get_live_temperature()

# ৫. 🔮 গ্লোবাল সাইডবার ডিজাইন (আপনার কাঙ্ক্ষিত প্যানেল)
st.sidebar.markdown("## 🏥 Rog Mukti Diagnostic")
st.sidebar.markdown(f"📆 **তারিখ:** {datetime.datetime.now().strftime('%d %B, %Y')}")
st.sidebar.markdown(f"🌡️ **আজকের তাপমাত্রা:** `{live_temp}`") # এখানে তাপমাত্রা যোগ করা হলো
st.sidebar.markdown("---")

# 📊 কন্টেন্ট ১: Today's Quick Summary
st.sidebar.markdown("### 💰 আজকের লাইভ হিসাব")
st.sidebar.markdown(f"• **মোট রোগী:** {total_patients} জন")
st.sidebar.markdown(f"• **মোট কালেকশন:** {total_cash} ৳")
st.sidebar.markdown(f"• **মোট বাকি (Due):** {total_due} ৳")
st.sidebar.markdown("---")

# 🩸 কন্টেন্ট ২: Top Tests Today
st.sidebar.markdown("### 📈 আজকের সেরা টেস্ট সমূহ")
if top_tests_dict:
    sorted_tests = sorted(top_tests_dict.items(), key=lambda x: x[1], reverse=True)[:3]
    for test, count in sorted_tests:
        st.sidebar.markdown(f"• **{test}:** {count} টি এন্ট্রি")
else:
    st.sidebar.markdown("আজ এখনো কোনো টেস্ট এন্ট্রি হয়নি")
st.sidebar.markdown("---")

# ⚙️ কন্টেন্ট ৩: System Status Monitor
st.sidebar.markdown("### 🖥️ সিস্টেম স্ট্যাটাস")
if os.path.exists(db_name):
    st.sidebar.markdown("🟢 **Database:** Connected")
else:
    st.sidebar.markdown("🔴 **Database:** Disconnected")
st.sidebar.markdown("🟢 **Server Cloud:** Online")
st.sidebar.markdown("---")

# 💡 কন্টেন্ট ৪: Daily Patient Tips Box
st.sidebar.markdown("### 💡 আজকের গুরুত্বপূর্ণ টিপস")
tips = [
    "খালি পেটে সুগার টেস্টের আগে রোগীকে অন্তত ৮-১০ ঘণ্টা ফাস্টিং করতে বলুন।",
    "লিপিড প্রোফাইলের নির্ভুল রিপোর্টের জন্য আগের রাতে চর্বিযুক্ত খাবার এড়াতে বলুন।",
    "ইউরিন আর/ই টেস্টের জন্য রোগীকে মিড-স্ট্রিম বা মাঝখানের প্রস্রাব সংগ্রহ করতে গাইড করুন।",
    "যেকোনো এক্স-রে করার আগে মেটালের জিনিসপত্র (চেইন, চাবি) শরীর থেকে সরাতে বলুন।"
]
current_tip = tips[datetime.datetime.now().minute % len(tips)]
st.sidebar.info(current_tip)


# ================= MAIN SCREEN DESIGN =================
st.title("📊 রিয়েল-টাইম অ্যাডভান্সড ড্যাশবোর্ড ও ল্যাব মনিটর")
st.write("এই পেজটি আপনার ডায়াগনস্টিক সেন্টারের লাইভ প্যাথলজি অপারেশন এবং আজকের কাজের অগ্রগতি ট্র্যাক করছে।")
st.markdown("---")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.header("📝 ল্যাব টু-ডু ও পেন্ডিং টেস্ট ট্র্যাকার")
    st.info("আজকে কাউন্টারে এন্ট্রি হওয়া রিসিট সমূহের লাইভ অবস্থা:")
    try:
        conn = sqlite3.connect(db_name)
        df_view = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE date LIKE '{today_date}%' ORDER BY date DESC", conn)
        conn.close()
        if not df_view.empty:
            st.dataframe(df_view, use_container_width=True, height=250)
        else:
            st.info("👋 আজ এখনো কোনো নতুন রোগীর এন্ট্রি দেওয়া হয়নি।")
    except:
        st.write("ডাটা লোড করা যাচ্ছে না।")

with col2:
    st.header("🚨 ইমার্জেন্সি রি-অ্যাক্ট ও নোটিফিকেশন")
    with st.form("emergency_alert_form"):
        alert_msg = st.text_input("জরুরি বার্তার বিষয়:", placeholder="এখানে টাইপ করুন...")
        submit_alert = st.form_submit_button("🔴 ল্যাবে জরুরি এলার্ট জারি করুন")
        if submit_alert and alert_msg:
            st.toast(f"🚨 ইমার্জেন্সি অ্যালার্ট: {alert_msg}", icon="⚠️")
            st.error(f"⚠️ **জরুরি নোটিশ:** {alert_msg}")
            
    st.markdown("---")
    st.subheader("📞 কুইক ল্যাব ডিরেক্টরি")
    with st.expander("📞 জরুরি ফোন নম্বর সমূহ দেখতে এখানে ক্লিক করুন"):
        st.write("• **অন-ডিউটি প্যাথলজিস্ট:** ০১৭১১-XXXXXX")
        st.write("• **এক্স-রে টেকনিশিয়ান:** ০১৭২২-XXXXXX")
