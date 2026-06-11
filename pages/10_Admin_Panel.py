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
    tables = [row for row in cursor.fetchall()]
    for t in tables:
        if 'bill' in t.lower() or 'patient' in t.lower() or 'record' in t.lower():
            table_name = t
            break
    conn.close()
except:
    pass

# ৬. ট্যাব ভিত্তিক অল-ইন-ওয়ান মাস্টার নেভিগেশন কন্ট্রোল
tab1, tab2, tab3 = st.tabs([
    "🧪 টেস্ট ও রেট চার্ট", 
    "🗑️ রিসিট ডিলিট প্যানেল", 
    "📝 পেশেন্ট ইনফো ও পেমেন্ট এডিটর"
])

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
        df_bills = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        bill_col = df_bills.columns[0] # প্রথম কলামকে আইডি/বিল নং ধরা হলো
        df_bills = df_bills.sort_values(by=bill_col, ascending=False)
    except:
        df_bills = pd.DataFrame()
    conn.close()

    if not df_bills.empty:
        col_del1, col_del2 = st.columns(2, gap="large")
        with col_del1:
            with st.form("delete_bill_form"):
                bill_to_delete = st.selectbox("ডিলিট করার জন্য বিল নম্বর সিলেক্ট করুন:", [""] + list(df_bills[bill_col].astype(str)))
                confirm_delete = st.checkbox("আমি নিশ্চিত যে আমি এই রিসিটটি চিরতরে মুছে ফেলতে চাই।")
                delete_b_btn = st.form_submit_button("💥 রিসিটটি পুরোপুরি ডিলিট করুন")
                
                if delete_b_btn and bill_to_delete:
                    if confirm_delete:
                        conn = sqlite3.connect(db_name)
                        cursor = conn.cursor()
                        cursor.execute(f"DELETE FROM {table_name} WHERE {bill_col} = ?", (int(bill_to_delete),))
                        conn.commit()
                        conn.close()
                        st.success(f"🗑️ বিল নম্বর {bill_to_delete} সফলভাবে মুছে ফেলা হয়েছে!")
                        st.rerun()
                    else:
                        st.warning("⚠️ নিশ্চিত করতে টিক চিহ্ন দিন।")
        with col_del2:
            st.write("📋 **বর্তমান রিসিট সমূহের তালিকা:**")
            st.dataframe(df_bills, use_container_width=True, height=250)
    else:
        st.info("💡 ডাটাবেজে কোনো বিলের রেকর্ড খুঁজে পাওয়া যায়নি।")

# ================= TAB 3: পেশেন্ট ইনফো ও পেমেন্ট এডিটর =================
with tab3:
    st.subheader("✍️ রোগীর তথ্য, ডিসকাউন্ট, অ্যাডভান্স ও বকেয়া (Due) সংশোধন ফর্ম")
    st.info("💡 কোনো রোগীর নাম ভুল হলে বা কেউ বকেয়া টাকা পরিশোধ করলে এখান থেকে সরাসরি আপডেট করতে পারবেন।")
    
    conn = sqlite3.connect(db_name)
    try:
        df_edit_patients = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        cols = df_edit_patients.columns
    except:
        df_edit_patients = pd.DataFrame()
        cols = []
    conn.close()

    if not df_edit_patients.empty:
        # ১. রোগী নির্বাচন
        selected_bill = st.selectbox("যে রোগীর তথ্য সংশোধন করতে চান তার বিল নম্বরটি সিলেক্ট করুন:", [""] + list(df_edit_patients[cols[0]].astype(str)), key="edit_select_box")
        
        if selected_bill:
            # নির্বাচিত রোগীর বর্তমান ডাটা তুলে আনা
            patient_row = df_edit_patients[df_edit_patients[cols[0]].astype(str) == selected_bill].iloc[0]
            
            st.markdown("---")
            st.write(f"🔄 **বিল নম্বর {selected_bill} এর তথ্য সংশোধন করুন:**")
            
            # ডাটাবেজের কলামের সংখ্যার ওপর ভিত্তি করে ডাইনামিক ইনপুট ফর্ম তৈরি
            with st.form("patient_data_edit_form"):
                updated_values = {}
                form_cols = st.columns(2)
                
                for idx, col_name in enumerate(cols):
                    # ১ম কলাম আইডি/বিল নং হওয়ায় এটি এডিট করা যাবে না
                    if idx == 0:
                        updated_values[col_name] = patient_row[col_name]
                        continue
                        
                    current_val = patient_row[col_name]
                    col_side = form_cols[0] if idx % 2 == 0 else form_cols[1]
                    
                    # ডাটা টাইপ অনুযায়ী ইনপুট বক্স দেখানো
                    if isinstance(current_val, (int, float)):
                        updated_values[col_name] = col_side.number_input(f"{col_name} সংশোধন করুন:", value=float(current_val))
                    else:
                        updated_values[col_name] = col_side.text_input(f"{col_name} সংশোধন করুন:", value=str(current_val))
                
                save_changes = st.form_submit_button("💾 রোগীর সংশোধিত তথ্য ডাটাবেজে সেভ করুন")
                
                if save_changes:
                    conn = sqlite3.connect(db_name)
                    cursor = conn.cursor()
                    
                    # SQL UPDATE কুয়েরি তৈরি করা
                    set_clause = ", ".join([f"{c} = ?" for c in cols[1:]])
                    query_params = [updated_values[c] for c in cols[1:]] + [updated_values[cols[0]]]
                    
                    cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {cols[0]} = ?", query_params)
                    conn.commit()
                    conn.close()
                    
                    st.success(f"🎉 বিল নম্বর {selected_bill} এর সমস্ত তথ্য (নাম/মোবাইল/ডিসকাউন্ট/ডিউ) সফলভাবে আপডেট হয়েছে!")
                    st.rerun()
        
        st.markdown("---")
        st.write("📋 **বর্তমান ডাটাবেজের লাইভ তালিকা:**")
        st.dataframe(df_edit_patients, use_container_width=True, height=200)
    else:
        st.info("💡 ডাটাবেজে এই মুহূর্তে কোনো রোগীর তথ্য নেই।")
