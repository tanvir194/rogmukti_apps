import streamlit as st

# আপনার গোপন পাসওয়ার্ড (এটি আপনি চাইলে পরিবর্তন করতে পারেন)
ADMIN_PASSWORD = "rogmukti_admin"

if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

# সঠিক পাসওয়ার্ড না দেওয়া পর্যন্ত পেজটি লক থাকবে
if not st.session_state.admin_auth:
    st.warning("🔒 এই পেজটি লক করা আছে। দেখার জন্য অ্যাডমিন পাসওয়ার্ড দিন।")
    password_box = st.text_input("🔑 পাসওয়ার্ড লিখুন:", type="password", key=f"lock_{st.runtime.scriptrunner.script_run_context.get_script_run_context().page_script_hash}")
    
    if st.button("🔓 আনলক করুন", type="primary", key=f"btn_{st.runtime.scriptrunner.script_run_context.get_script_run_context().page_script_hash}"):
        if password_box == ADMIN_PASSWORD:
            st.session_state.admin_auth = True
            st.success("🎉 সফলভাবে আনলক হয়েছে!")
            st.rerun()
        else:
            st.error("❌ ভুল পাসওয়ার্ড!")
    st.stop() # 🛑 সঠিক পাসওয়ার্ড না দিলে নিচের বাকি কোড রান হবে না  
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# সিকিউরিটি চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

st.title("🩺 ডাক্তার রেফারেল ফি ও কমিশন ক্যালকুলেটর")
st.write("---")

conn = sqlite3.connect("rogmukti_clinic_fix.db")

try:
    # ডাটাবেজ থেকে বিলের রেকর্ড এবং ডাক্তারের তালিকা রিড করা
    df = pd.read_sql_query("SELECT id, patient_name, doctor, total_amount, billing_date FROM billing_records", conn)
    
    if not df.empty:
        # তারিখ ফরম্যাট ঠিক করা
        df['billing_date'] = pd.to_datetime(df['billing_date'], errors='coerce')
        df = df.dropna(subset=['billing_date'])
        
        # ১. ফিল্টার সেকশন (ডাক্তার, শুরু ও শেষের তারিখ)
        st.subheader("🔍 ফিল্টার ও ক্যালকুলেশন প্যারামিটার")
        
        col1, col2 = st.columns(2)
        with col1:
            # ডাটাবেজে থাকা ইউনিক ডাক্তারদের লিস্ট ড্রপডাউনে আনা
            doctor_list = sorted(df['doctor'].unique().tolist())
            selected_doctor = st.selectbox("🩺 ডাক্তার সিলেক্ট করুন:", doctor_list)
        
        with col2:
            # তারিখের রেঞ্জ সিলেক্ট করার ইনপুট (যেমন: ১ তারিখ থেকে ১০ তারিখ)
            today = datetime.now().date()
            start_date = st.date_input("📅 শুরুর তারিখ:", datetime(today.year, today.month, 1).date())
            end_date = st.date_input("📅 শেষের তারিখ:", today)
            
        if start_date > end_date:
            st.error("⚠️ শুরুর তারিখ অবশ্যই শেষের তারিখের চেয়ে ছোট বা সমান হতে হবে!")
            st.stop()
            
        # ডাটাবেজের ডাটা ফিল্টার করা (নির্দিষ্ট ডাক্তার এবং তারিখের রেঞ্জ অনুযায়ী)
        filtered_df = df[
            (df['doctor'] == selected_doctor) & 
            (df['billing_date'].dt.date >= start_date) & 
            (df['billing_date'].dt.date <= end_date)
        ]
        
        st.markdown("---")
        
        # ২. পার্সেন্টেজ ইনপুট ও লাইভ ক্যালকুলেশন
        st.subheader("💰 কমিশন পার্সেন্টেজ (%) এন্ট্রি")
        
        total_business = filtered_df['total_amount'].sum() if not filtered_df.empty else 0.0
        
        box1, box2 = st.columns(2)
        with box1:
            st.info(f"📊 সিলেক্ট করা সময়ে **{selected_doctor}** এর মোট বিল এসেছে: **{total_business:,.2f} ৳**")
            # পার্সেন্টেজ ইনপুট বক্স
            commission_pct = st.number_input("🔗 কত পার্সেন্ট (%) কমিশন দিতে চান?:", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
        
        # অটোমেটিক রেফার ফি হিসাব
        calculated_commission = (total_business * commission_pct) / 100.0
        
        with box2:
            st.metric(label=f"🎯 অটো প্রদেয় রেফার ফি ({commission_pct}%)", value=f"{calculated_commission:,.2f} ৳")
            st.caption(f"{start_date} থেকে {end_date} পর্যন্ত সময়ের মোট হিসাব")

        st.markdown("---")
        
        # ৩. রোগীর বিস্তারিত তালিকা দেখানো
        st.subheader(f"📋 {selected_doctor} এর রোগীদের বিস্তারিত তালিকা")
        if not filtered_df.empty:
            st.success(f"📈 এই সময়ে মোট {len(filtered_df)} টি বিল পাওয়া গেছে।")
            
            # টেবিলটি সুন্দরভাবে সাজানো
            display_df = filtered_df.copy()
            display_df['billing_date'] = display_df['billing_date'].dt.strftime('%Y-%m-%d')
            display_df = display_df.rename(columns={
                'id': 'বিল নং', 'patient_name': 'রোগীর নাম', 
                'total_amount': 'মোট বিল (৳)', 'billing_date': 'তারিখ'
            })
            
            st.dataframe(display_df[['বিল নং', 'তারিখ', 'রোগীর নাম', 'মোট বিল (৳)']], use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ এই সময়ের মধ্যে এই ডাক্তারের কোনো রোগীর বিল তৈরি করা হয়নি।")
            
    else:
        st.info("ℹ️ ডাটাবেজে এখনো কোনো রোগীর বিলের ডাটা সেভ করা হয়নি।")
except Exception as e:
    st.error(f"❌ ডাটা লোড হতে সমস্যা হচ্ছে। এরর বিবরণ: {e}")

conn.close()
            
