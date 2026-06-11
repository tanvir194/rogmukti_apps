import streamlit as st
import pandas as pd
import sqlite3
import datetime

def show_live_sidebar():
    db_name = "rogmukti_clinic_fix.db"
    table_name = "billing_records"
    total_cash = 0
    total_due = 0
    total_patients = 0
    top_tests_dict = {}

    try:
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(db_name) as conn:
            df_today = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE date LIKE '{today_date}%'", conn)
        
        if not df_today.empty:
            total_patients = len(df_today)
            cash_col = [c for c in df_today.columns if 'total' in c.lower() or 'amount' in c.lower() or 'paid' in c.lower() or 'net_paid' in c.lower()]
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

    # সম্পূর্ণ সাইডবার ডিজাইন
    with st.sidebar:
        st.markdown("## 🏥 Rog Mukti Diagnostic")
        st.markdown(f"📅 **তারিখ:** {datetime.datetime.now().strftime('%d %B, %Y')}")
        st.markdown(f"🔄 **লাইভ মনিটর:** প্রতি ১০ সেকেন্ডে অটো-আপডেট")
        st.markdown("---")
        
        # ১. আজকের লাইভ হিসাব
        st.markdown("### 📝 আজকের লাইভ হিসাব")
        st.success(f"👥 **মোট রোগী:** {total_patients} জন")
        st.info(f"💰 **মোট কালেকশন:** {int(total_cash)} ৳")
        st.error(f"⚠️ **মোট বাকি (Due):** {int(total_due)} ৳")
        st.markdown("---")
        
        # ২. ল্যাব টু-ডু ও প্রগ্রেস
        st.markdown("### ⏳ ল্যাব টু-ডু ও প্রগ্রেস")
        progress_val = 65  # উদাহরণ প্রগ্রেস মান
        st.progress(progress_val / 100)
        st.caption(f"রিপোর্ট তৈরির অগ্রগতি: {progress_val}%")
        st.markdown("---")
        
        # ৩. ক্রিটিক্যাল ল্যাব অ্যালার্ট
        st.markdown("### ⚠️ ক্রিটিক্যাল ল্যাব অ্যালার্ট")
        st.error("🚨 **ID: P-2041** - Hb: 5.2 (কম)")
        st.error("🚨 **ID: P-2055** - Sugar: 24.1 (বেশি)")
        st.markdown("---")
        
        # ৪. আজকের সেরা টেস্ট সমূহ (ছোট টেবিল আকারে)
        st.markdown("### 📈 আজকের সেরা টেস্ট সমূহ")
        if top_tests_dict:
            df_top_tests = pd.DataFrame(list(top_tests_dict.items()), columns=['টেস্ট', 'টি']).sort_values(by='টি', ascending=False)
            st.dataframe(df_top_tests, use_container_width=True, hide_index=True, height=120)
        else:
            st.caption("আজকে এখনো কোনো টেস্ট এন্ট্রি হয়নি।")
        st.markdown("---")
        
        # ৫. ডক্টর রেফারেল ট্র্যাকার (ছোট টেবিল আকারে)
        st.markdown("### 🩺 ডক্টর রেফারেল")
        ref_data = pd.DataFrame({
            'ডাক্তার': ['ডাঃ আরিফুর', 'ডাঃ নুসরাত', 'ডাঃ হাসান'],
            'রোগী': [int(total_patients*0.5), int(total_patients*0.3), int(total_patients*0.2)]
        })
        st.table(ref_data)
        st.markdown("---")
        
        # ৬. ঘণ্টাভিত্তিক কালেকশন ছোট ট্রেন্ড চার্ট
        st.markdown("### 📊 কালেকশন ট্রেন্ড")
        chart_data = pd.DataFrame({
            '৳': [total_cash * 0.2, total_cash * 0.5, total_cash]
        }, index=['সকাল', 'দুপুর', 'রাত'])
        st.line_chart(chart_data, height=120)
