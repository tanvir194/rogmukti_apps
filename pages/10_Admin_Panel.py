import streamlit as st
import pandas as pd
import sqlite3
import os

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Admin Super Control", layout="wide")

# ২. লগইন ট্র্যাকিং সেশন তৈরি
if 'admin_panel_logged_in' not in st.session_state:
    st.session_state.admin_panel_logged_in = False

st.title("🎛️ Rog Mukti App Super Control Center")
st.markdown("---")

# ৩. পাসওয়ার্ড প্রটেকশন লজিক (Password: tanvir)
if not st.session_state.admin_panel_logged_in:
    st.subheader("🔒 এই পেজটি পাসওয়ার্ড দ্বারা সুরক্ষিত")
    input_password = st.text_input("পাসওয়ার্ড লিখুন:", type="password", key="panel_pass_input")
    if st.button("কন্ট্রোল প্যানেল আনলক করুন"):
        if input_password == "tanvir":
            st.session_state.admin_panel_logged_in = True
            st.rerun()
        else:
            st.error("❌ ভুল পাসওয়ার্ড!")
    st.stop()

st.success("🔓 আপনি বর্তমানে মাস্টার অ্যাডমিন হিসেবে লগইন আছেন।")
if st.button("🔴 প্যানেলটি পুনরায় লক করুন (Logout)"):
    st.session_state.admin_panel_logged_in = False
    st.rerun()

st.markdown("---")

# ৪. ডাটাবেজ ফাইল অটো-ডিটেক্ট করা
db_name = "database.db"
for file in os.listdir('.'):
    if file.endswith('.db'):
        db_name = file

# ৫. ডাটাবেজের আসল বিল টেবিলের নাম অটো-খুঁজে বের করার লজিক
table_name = "billing_records" # ডিফল্ট
try:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    # বিল বা পেশেন্ট সম্পর্কিত টেবিল খোঁজা
    for t in tables:
        if 'bill' in t.lower() or 'patient' in t.lower() or 'record' in t.lower():
            table_name = t
            break
    conn.close()
except:
    pass

# ৬. ট্যাব ভিত্তিক অল-ইন-ওয়ান মাস্টার মেনু
tab1, tab2 = st.tabs(["🧪 টেস্ট ও রেট চার্ট কন্ট্রোল", "🗑️ রিসিট ডিলিট প্যানেল"])

# ================= TAB 1: টেস্ট কন্ট্রোল =================
with tab1:
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("📝 নতুন টেস্ট যোগ ও মূল্য পরিবর্তন")
        with st.form("test_edit_form", clear_on_submit=True):
            t_name = st.text_input("টেস্টের নাম লিখুন:")
            t_price = st.number_input("টেস্টের মূল্য (BDT):", min_value=0.0, step=10.0)
            submit_btn = st.form_submit_button("অ্যাপের ডাটাবেজে আপডেট করুন")
            if submit_btn and t_name:
                conn = sqlite3.connect(db_name)
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS test_prices (test_name TEXT PRIMARY KEY, price REAL)")
                cursor.execute("INSERT OR REPLACE INTO test_prices VALUES (?, ?)", (t_name, t_price))
                conn.commit()
                conn.close()
                st.success("🎉 টেস্ট সফলভাবে আপডেট হয়েছে!")
                st.rerun()
    with col2:
        st.subheader("📋 লাইভ রেট চার্ট")
        conn = sqlite3.connect(db_name)
        try:
            df_tests = pd.read_sql_query("SELECT test_name AS 'টেস্টের নাম', price AS 'মূল্য (BDT)' FROM test_prices", conn)
        except:
            df_tests = pd.DataFrame(columns=['টেস্টের নাম', 'মূল্য (BDT)'])
        conn.close()
        st.dataframe(df_tests, use_container_width=True, height=200)

# ================= TAB 2: রিসিট ডিলিট প্যানেল =================
with tab2:
    st.subheader("❌ ভুল বা বাতিল রিসিট/বিল চিরতরে ডিলিট করার ফর্ম")
    
    conn = sqlite3.connect(db_name)
    try:
        # স্বয়ংক্রিয়ভাবে খুঁজে পাওয়া টেবিল থেকে ডাটা রিড করা
        df_bills = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        # কলামের নাম যাই হোক, প্রথম কলামটিকে বিল নম্বর হিসেবে ধরা হবে
        bill_col = df_bills.columns[0] 
        df_bills = df_bills.sort_values(by=bill_col, ascending=False)
    except:
        df_bills = pd.DataFrame()
    conn.close()

    if not df_bills.empty:
        col_del1, col_del2 = st.columns()
        with col_del1:
            with st.form("delete_bill_form"):
                bill_to_delete = st.selectbox("ডিলিট করার জন্য বিল/রিসিট নম্বর সিলেক্ট করুন:", [""] + list(df_bills[bill_col].astype(str)))
                confirm_delete = st.checkbox("আমি নিশ্চিত যে আমি এই রিসিটটি চিরতরে মুছে ফেলতে চাই।")
                delete_b_btn = st.form_submit_button("💥 রিসিটটি পুরোপুরি ডিলিট করুন")
                
                if delete_b_btn and bill_to_delete:
                    if confirm_delete:
                        conn = sqlite3.connect(db_name)
                        cursor = conn.cursor()
                        # সঠিক টেবিল থেকে ডিলিট লজিক
                        cursor.execute(f"DELETE FROM {table_name} WHERE {bill_col} = ?", (int(bill_to_delete),))
                        conn.commit()
                        conn.close()
                        st.success(f"🗑️ বিল নম্বর {bill_to_delete} সফলভাবে ডাটাবেজ থেকে মুছে ফেলা হয়েছে!")
                        st.rerun()
                    else:
                        st.warning("⚠️ নিশ্চিত করতে টিক চিহ্ন দিন।")
        with col_del2:
            st.write("📋 **বর্তমান রিসিট সমূহের তালিকা:**")
            st.dataframe(df_bills, use_container_width=True, height=250)
    else:
        st.info("💡 এই মুহূর্তে ডাটাবেজে কোনো রিসিট বা বিলের রেকর্ড খুঁজে পাওয়া যায়নি। 'Patient Entry' পেজে গিয়ে অন্তত ১টি নতুন বিল সেভ করলেই এখানে তালিকা চলে আসবে।")
