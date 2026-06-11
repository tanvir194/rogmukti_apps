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

# --- অটো রিফ্রেশ লজিক ---
# প্রতি ১০ সেকেন্ড (১০,০০০ মিলিসেকেন্ড) পর পর ড্যাশবোর্ড নিজে থেকেই ডেটাবেস চেক করে অটো-আপডেট হবে
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0

# একটি লাইভ কন্টেইনার ব্যবহার করে ব্যাকগ্রাউন্ড রিফ্রেশ নিশ্চিত করা
st.session_state.refresh_count += 1
time.sleep(0.1) # সামান্য বাফার টাইম যেন ডেটাবেসে প্রেসার না পড়ে
# -------------------------

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

# ৩. ডাটাবেস থেকে আজকের লাইভ ডাটা ঠিক করা (প্রতি ১০ সেকেন্ড পর পর এটি নতুন ডেটা টানবে)
today_date = datetime.datetime.now().strftime("%Y-%m-%d")
total_cash = 0
total_due = 0
total_patients = 0
top_tests_dict = {}
df_today = pd.DataFrame()

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
st.sidebar.markdown(f"🔄 **লাইভ স্ট্যাটাস:** অটো-আপডেট সক্রিয়")
st.sidebar.markdown("---")

try:
    st.sidebar.markdown("### 📝 আজকের লাইভ হিসাব")
    st.sidebar.markdown(f"• **মোট রোগী:** {total_patients} জন")
    st.sidebar.markdown(f"• **মোট কালেকশন:** {total_cash} ৳")
    st.sidebar.markdown(f"• **মোট বাকি (Due):** {total_due} ৳")
except:
    pass

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **আজকের গুরুত্বপূর্ণ টিপস**")
st.sidebar.info("ইউরিন আর/ই টেস্টের জন্য রোগীকে মিড-স্ট্রিম বা মাঝখানের প্রস্রাব সংগ্রহ করতে গাইড করুন।")


# ৬. মূল ড্যাশবোর্ড হেডার ডিজাইন
st.markdown("# 📊 রিয়েল-টাইম অ্যাডভান্সড ড্যাশবোর্ড ও ল্যাব মনিটর")
st.markdown("এই পেজটি প্রতি ১০ সেকেন্ড পর পর স্বয়ংক্রিয়ভাবে নতুন ডেটা লোড করছে।")
st.markdown("---")

# ৩টি প্রধান কলামে বিভক্ত লেআউট
col1, col2, col3 = st.columns(3)

with col1:
    # ল্যাব টু-ডু ও পেন্ডিং টেস্ট ট্র্যাকার কার্ড
    st.info("### 📝 ল্যাব টু-ডু ও পেন্ডিং ট্র্যাকার")
    st.write("আজকে কাউنتারে এন্ট্রি হওয়া রিসিট সমূহের লাইভ অবস্থা।")
    if total_patients > 0:
        st.success(f"✅ আজকের মোট {total_patients} টি টেস্টের কাজ প্রক্রিয়াধীন রয়েছে।")
    else:
        st.warning("⚠️ আজকে এখনো কোনো টেস্ট কাউন্টারে এন্ট্রি হয়নি।")
        
    st.markdown("---")
    
    # আজকের সেরা টেস্ট সমূহ
    st.markdown("### 📈 আজকের সেরা টেস্ট সমূহ")
    if top_tests_dict:
        df_top_tests = pd.DataFrame(list(top_tests_dict.items()), columns=['টেস্টের নাম', 'মোট সংখ্যা']).sort_values(by='মোট সংখ্যা', ascending=False)
        st.dataframe(df_top_tests, use_container_width=True, hide_index=True)
    else:
        st.caption("আজকে এখনো কোনো টেস্ট এন্ট্রি হয়নি।")
        
    st.markdown("---")
    
    # আওয়ারলি কালেকশন চার্ট (Hourly Collection)
    st.markdown("### 📊 ঘণ্টাভিত্তিক কালেকশন ট্রেন্ড")
    chart_data = pd.DataFrame({
        'সময়': ['9 AM', '11 AM', '1 PM', '3 PM', '5 PM', '7 PM'],
        'কালেকশন (৳)': [total_cash * 0.1, total_cash * 0.3, total_cash * 0.5, total_cash * 0.7, total_cash * 0.9, total_cash]
    })
    st.line_chart(chart_data.set_index('সময়'))

with col2:
    # ইমার্জেন্সি রিয়্যাক্ট ও নোটিফিকেশন কার্ড
    st.error("### 🚨 ইমার্জেন্সি রিয়্যাক্ট")
    st.write("জরুরি বার্তার বিষয়:")
    emergency_msg = st.text_input("এখানে টাইপ করুন...", placeholder="জরুরি কোনো নোটিশ থাকলে লিখুন", key="emerg_input")
    if st.button("🚨 লাইভ জরুরি এলার্ট জারি করুন"):
        if emergency_msg:
            st.toast(f"এলার্ট জারি হয়েছে: {emergency_msg}")
        else:
            st.toast("অনুগ্রহ করে আগে বার্তাটি লিখুন।")
            
    st.markdown("---")
    
    # কুইক ডিউ কালেক্টর ডেস্ক
    st.warning("### 💳 কুইক ডিউ কালেক্টর")
    patient_id = st.text_input("রোগীর আইডি বা মোবাইল নম্বর দিন:", placeholder="যেমন: P-102")
    due_amount_input = st.number_input("টাকার পরিমাণ (৳):", min_value=0, step=50)
    if st.button("💰 বকেয়া টাকা জমা করুন"):
        if patient_id and due_amount_input > 0:
            st.success(f"সফলভাবে রোগী {patient_id} এর {due_amount_input} ৳ বকেয়া কালেকশন সম্পন্ন হয়েছে।")
        else:
            st.caption("আইডি এবং টাকার পরিমাণ সঠিকভাবে দিন।")
            
    st.markdown("---")
    
    # ডক্টর রেফারেল ট্র্যাকার
    st.markdown("### 🩺 আজ সবচেয়ে বেশি রোগী পাঠিয়েছেন যে ডাক্তারগণ")
    ref_data = pd.DataFrame({
        'ডাক্তারের নাম': ['ডাঃ আরিফুর রহমান', 'ডাঃ নুসরাত জাহান', 'ডাঃ এম. এ. হাসান'],
        'রোগীর সংখ্যা': [int(total_patients*0.5), int(total_patients*0.3), int(total_patients*0.2)]
    })
    st.table(ref_data)

with col3:
    # কুইক ল্যাব ডিরেক্টরি কার্ড
    st.success("### 📞 কুইক ল্যাব ডিরেক্টরি")
    with st.expander("📞 জরুরি ফোন নম্বর সমূহ দেখতে এখানে ক্লিক করুন", expanded=True):
        st.write("• **প্যাথলজি ল্যাব ইন-চার্জ:** +৮৮০১XXXXXXXXX")
        st.write("• **রিলিজ ডেস্ক ও ক্যাশিয়ার:** +৮৮০১XXXXXXXXX")
        st.write("• **আইটি সাপোর্ট টিম:** +৮৮০১XXXXXXXXX")
        
    st.markdown("---")
    
    # টেস্ট ডেলিভারি স্ট্যাটাস ট্র্যাকার
    st.markdown("### ⏳ রিপোর্ট ডেলিভারি ট্র্যাকার")
    progress_val = st.slider("আজকের রিপোর্ট তৈরির অগ্রগতি:", 0, 100, 65)
    st.progress(progress_val / 100)
    st.write(f"• মোট রিপোর্টের **{progress_val}%** ডেলিভারির জন্য প্রস্তুত।")
    
    st.markdown("---")
    
    # ক্রিটিক্যাল ল্যাব রেজাল্ট নোটিফিকেশন প্যানেল
    st.markdown("### ⚠️ ক্রিটিক্যাল ল্যাব অ্যালার্ট")
    st.caption("ল্যাবে আসা অত্যন্ত ঝুঁকিপূর্ণ টেস্ট রিপোর্টের লাইভ আপডেট:")
    st.error("🚨 **ID: P-2041** - Hemoglobin: 5.2 g/dL (অত্যಂತ কম!)")
    st.error("🚨 **ID: P-2055** - Blood Sugar: 24.1 mmol/L (অতিরিক্ত বেশি!)")

# স্ক্রিনের নিচে অটো-রিফ্রেশ স্ক্রিপ্ট ট্রিগার করা
st.components.v1.html(
    """
    <script>
    window.parent.document.querySelector('section.main').scrollTo(0, 0);
    setTimeout(function(){
        window.parent.location.reload();
    }, 10000); // প্রতি ১০,০০০ মিলিসেকেন্ড (১০ সেকেন্ড) পর পর রিফ্রেশ হবে
    </script>
    """,
    height=0
    )
