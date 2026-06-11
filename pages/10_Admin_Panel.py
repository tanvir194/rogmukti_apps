import streamlit as st
import pandas as pd
import sqlite3
import os
import datetime

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
    "📝 মাস্টার পেশেন্ট এন্ট্রি ও এডিটর"
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
        bill_col = df_bills.columns[0]
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

# ================= TAB 3: মাস্টার পেশেন্ট এন্ট্রি ও এডিটর =================
with tab3:
    st.subheader("🚀 লাইভ কাস্টম পেশেন্ট বিলিং ফর্ম (নতুন টেস্টের দামসহ)")
    st.info("💡 আপনার 'Patient Entry' পেজে কোনো নতুন টেস্টের নাম না আসলে, সরাসরি এই ফর্মটি পূরণ করে আপনি যেকোনো রোগীর বিল নিখুঁতভাবে সেভ করতে পারবেন।")
    
    # এডমিন প্যানেলের লাইভ টেস্ট ডাটা তুলে আনা
    conn = sqlite3.connect(db_name)
    try:
        df_live_t = pd.read_sql_query("SELECT test_name, price FROM test_prices", conn)
        live_tests = dict(zip(df_live_t['test_name'], df_live_t['price']))
    except:
        live_tests = {"CBC": 400.0, "Lipid Profile": 1000.0, "Blood Sugar": 150.0, "Urine RE": 250.0}
    conn.close()

    # মাস্টার ইনপুট ফর্ম ডিজাইন
    with st.form("master_patient_billing_form"):
        st.write("### 👤 পেশেন্ট ইনফরমেশন")
        col_m1, col_m2 = st.columns(2)
        adm_p_name = col_m1.text_input("পেশেন্টের নাম (Name of the PT) *")
        adm_p_age = col_m2.number_input("বয়স (Age)", min_value=1, max_value=120, value=25)

        col_m3, col_m4 = st.columns(2)
        adm_p_phone = col_m3.text_input("মোবাইল নম্বর (Phone)")
        adm_p_ref = col_m4.selectbox("ডাক্তার সিলেক্ট করুন (Refd By)", ["ডাঃ সাইদুল ইসলাম", "অন্যান্য"])

        st.write("### 🧪 টেস্ট সিলেকশন")
        # 🚀 এডমিন প্যানেলের লাইভ রঙিন টেস্টের তালিকা ড্রপডাউনে আনা হলো
        adm_selected_tests = st.multiselect("১ বা একাধিক টেস্ট সিলেক্ট করুন:", list(live_tests.keys()))
        
        # পেমেন্ট ক্যালকুলেশন
        st.write("### 💰 পেমেন্ট ও ডিসকাউন্ট")
        col_p1, col_p2 = st.columns(2)
        adm_discount_pct = col_p1.number_input("ডিসকাউন্ট (Discount %)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
        adm_advance = col_p2.number_input("অগ্র命 পরিশোধ (Advance Paid)", min_value=0.0, value=0.0, step=50.0)
        
        adm_save_btn = st.form_submit_button("🔥 রোগীর বিল সরাসরি ডাটাবেজে সেভ করুন")
        
        if adm_save_btn:
            if adm_p_name and adm_selected_tests:
                # হিসাব লজিক
                calc_total = sum([live_tests[t] for t in adm_selected_tests])
                calc_disc_tk = (calc_total * adm_discount_pct) / 100
                calc_due = calc_total - calc_disc_tk - adm_advance
                
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tests_string = ", ".join(adm_selected_tests)
                
                try:
                    conn = sqlite3.connect(db_name)
                    cursor = conn.cursor()
                    
                    # মূল অ্যাপের বিলিং টেবিলের কলাম স্ট্রাকচার অনুযায়ী ডাটা ইনসার্ট
                    cursor.execute(f'''
                        INSERT INTO {table_name} (patient_name, age, phone, ref_by, tests, total_amount, discount, advance, due_amount, date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (adm_p_name, int(adm_p_age), adm_p_phone, adm_p_ref, tests_string, calc_total, calc_disc_tk, adm_advance, calc_due, current_time))
                    
                    conn.commit()
                    conn.close()
                    st.success(f"🎉 চমৎকার! '{adm_p_name}' এর বিলটি নতুন টেস্টের সঠিক মূল্যসহ ডাটাবেজে সেভ হয়েছে। এখন আপনি সরাসরি 'Print Receipt' পেজে গিয়ে এটি প্রিন্ট করতে পারবেন।")
                except Exception as err:
                    st.error(f"ডাটাবেজ কলাম অমিল হওয়ার কারণে এরর: {err}")
            else:
                st.error("⚠️ দয়া করে রোগীর নাম এবং অন্তত একটি টেস্ট সিলেক্ট করুন।")
