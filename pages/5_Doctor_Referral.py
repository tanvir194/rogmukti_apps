import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# সিকিউরিটি চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

st.title("🩺 ডাক্তার রেফারেল ফি ও কমিশন ম্যানেজমেন্ট")

# ডাটাবেজ কানেকশন ও কলাম চেক
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# মূল টেবিলে ref_fee কলামটি আছে কি না তা নিশ্চিত করা (না থাকলে যোগ হবে)
try:
    c.execute("ALTER TABLE billing_records ADD COLUMN ref_fee REAL DEFAULT 0.0")
    conn.commit()
except sqlite3.OperationalError:
    pass
conn.close()

# ট্যাব সিস্টেম (১টি ফি ইনপুট বা আপডেট করার জন্য, আরেকটি টোটাল রিপোর্ট দেখার জন্য)
tab1, tab2 = st.tabs(["✍️ রেফার ফি এন্ট্রি/আপডেট", "📊 ডাক্তারদের মোট পাওনা রিপোর্ট"])

# --- ট্যাব ১: রেফার ফি এন্ট্রি/আপডেট সেকশন ---
with tab1:
    st.subheader("🔍 বিল নম্বর দিয়ে রেফার ফি সেট করুন")
    search_id = st.number_input("বিল নম্বর (Bill No / Invoice ID) দিন:", min_value=0, step=1, value=0)
    
    if search_id > 0:
        conn = sqlite3.connect("rogmukti_clinic_fix.db")
        c = conn.cursor()
        c.execute("SELECT id, patient_name, doctor, selected_tests, total_amount, ref_fee, billing_date FROM billing_records WHERE id = ?", (search_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            st.info(f"📋 **রোগীর নাম:** {row[1]} | 🩺 **রেফার করা ডাক্তার:** {row[2]} | 📅 **তারিখ:** {row[6]}")
            
            # টেস্টের নামগুলো কমা দিয়ে সুন্দর করে দেখানো
            tests_clean = row[3].replace('|', ', ')
            st.write(f"🔬 **টেস্টসমূহ:** {tests_clean}")
            st.write(f"💰 **মোট বিল:** {row[4]:.2f} ৳")
            
            current_ref_fee = float(row[5]) if row[5] is not None else 0.0
            st.warning(f"🚨 বর্তমানে এই বিলে রেফার ফি সেট করা আছে: **{current_ref_fee:.2f} ৳**")
            
            # নতুন রেফার ফি ইনপুট বক্স
            new_fee = st.number_input("এই বিলের জন্য রেফার ফি/কমিশন কত দিতে চান?:", min_value=0.0, value=current_ref_fee, step=50.0, key="new_ref_input")
            
            if st.button("💾 রেফারেল ফি সেভ করুন", type="primary"):
                conn = sqlite3.connect("rogmukti_clinic_fix.db")
                c = conn.cursor()
                c.execute("UPDATE billing_records SET ref_fee = ? WHERE id = ?", (new_fee, search_id))
                conn.commit()
                conn.close()
                st.success(f"✅ সফলভাবে আইডি #{search_id} এর বিলে {new_fee:.2f} ৳ রেফার ফি আপডেট হয়েছে!")
                st.rerun()
        else:
            st.error("⚠️ এই বিল নম্বরের কোনো রোগীর তথ্য পাওয়া যায়নি।")

# --- 📊 ট্যাব ২: ডাক্তারদের মোট পাওনা রিপোর্ট সেকশন ---
with tab2:
    st.subheader("🗓️ দৈনিক ও মাসিক ফিল্টার অনুযায়ী ডাক্তারদের মোট পাওনা")
    
    conn = sqlite3.connect("rogmukti_clinic_fix.db")
    try:
        df = pd.read_sql_query("SELECT doctor, ref_fee, billing_date FROM billing_records", conn)
        conn.close()
        
        if not df.empty:
            df['billing_date'] = pd.to_datetime(df['billing_date'], errors='coerce')
            df = df.dropna(subset=['billing_date'])
            
            filter_option = st.radio("ফিল্টার টাইপ সিলেক্ট করুন:", ["আজকের দিনের হিসাব", "চলতি মাসের হিসাব", "সব সময়ের মোট হিসাব"], horizontal=True)
            
            if filter_option == "আজকের দিনের হিসাব":
                filtered_df = df[df['billing_date'].dt.date == datetime.now().date()]
            elif filter_option == "চলতি মাসের হিসাব":
                filtered_df = df[(df['billing_date'].dt.month == datetime.now().month) & (df['billing_date'].dt.year == datetime.now().year)]
            else:
                filtered_df = df
                
            if not filtered_df.empty:
                # ডাক্তার অনুযায়ী গ্রুপ করে সামারি টেবিল তৈরি
                summary_df = filtered_df.groupby('doctor')['ref_fee'].sum().reset_index()
                summary_df = summary_df.rename(columns={'doctor': '🩺 ডাক্তারের নাম', 'ref_fee': '💰 মোট পাওনা রেফার ফি (টাকা)'})
                
                # মোট ক্যাশ আউট সামারি কার্ড
                st.metric("📊 ফিল্টার অনুযায়ী মোট প্রদেয় রেফার ফি", f"{summary_df['💰 মোট পাওনা রেফার ফি (টাকা)'].sum():,.2f} ৳")
                
                # সুন্দর ডাটা টেবিল
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
            else:
                st.warning("⚠️ এই ফিল্টারে কোনো রেফারেল ফির ডাটা পাওয়া যায়নি।")
        else:
            st.info("ℹ️ ডাটাবেজে এখনো কোনো বিলের রেকর্ড নেই।")
    except Exception as e:
        st.error(f"❌ রিপোর্ট লোড করা যাচ্ছে না। এরর: {e}")
          
