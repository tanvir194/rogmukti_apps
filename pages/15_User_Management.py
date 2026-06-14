import sys
import os
import streamlit as st
import sqlite3

# --- গ্লোবাল পাথ সেটআপ ও সাইডবার লোড ---
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from sidebar_monitor import show_live_sidebar
    show_live_sidebar()
except Exception:
    pass

# --- ডাটাবেজ কানেকশন ---
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# ইউজার টেবিল নিশ্চিত করা
c.execute("""CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY, 
    password TEXT,
    role TEXT DEFAULT 'staff')""")
conn.commit()

# --- পেজ ডিজাইন ---
st.title("🔐 স্টাফ ও পাসওয়ার্ড কন্ট্রোল")
st.write("এখান থেকে নতুন স্টাফ যোগ করুন এবং সবার পাসওয়ার্ড পরিবর্তন করুন।")
st.markdown("---")

tab1, tab2 = st.tabs(["➕ নতুন স্টাফ যোগ করুন", "🔄 পাসওয়ার্ড পরিবর্তন ও মডিফাই"])

# ট্যাব ১: নতুন স্টাফ তৈরি
with tab1:
    st.subheader("নতুন স্টাফ অ্যাকাউন্ট রেজিস্টার")
    new_user = st.text_input("নতুন ইউজারনেম (Username)", key="reg_u").strip()
    new_pass = st.text_input("পাসওয়ার্ড (Password)", type="password", key="reg_p")
    user_role = st.selectbox("রোল/পদবী", ["staff", "admin"], key="reg_r")
    
    if st.button("➕ স্টাফ অ্যাকাউন্ট তৈরি করুন", use_container_width=True):
        if new_user and new_pass:
            try:
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_user, new_pass, user_role))
                conn.commit()
                st.success(f"🎉 সফলতা! **{new_user}** তৈরি হয়েছে।")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("❌ এই ইউজারনেমটি ইতিমধ্যে সিস্টেমে আছে!")
        else:
            st.error("⚠️ দয়া করে ইউজারনেম এবং পাসওয়ার্ড দুটি ঘরই পূরণ করুন।")

# ট্যাব ২: মডিফাই এবং ডিলিট
with tab2:
    st.subheader("বর্তমান ইউজারদের পাসওয়ার্ড পরিবর্তন")
    c.execute("SELECT username FROM users")
    all_users = [row[0] for row in c.fetchall()]
    
    if all_users:
        selected_user = st.selectbox("কোন ইউজারের পাসওয়ার্ড মডিফাই করবেন?", all_users)
        updated_pass = st.text_input("নতুন পাসওয়ার্ড দিন", type="password", key="mod_p")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 পাসওয়ার্ড আপডেট করুন", use_container_width=True):
                if updated_pass:
                    c.execute("UPDATE users SET password = ? WHERE username = ?", (updated_pass, selected_user))
                    conn.commit()
                    st.success(f"✅ **{selected_user}** এর পাসওয়ার্ড আপডেট হয়েছে!")
                else:
                    st.error("⚠️ নতুন পাসওয়ার্ডের ঘরটি খালি রাখা যাবে না।")
                    
        with col2:
            if selected_user != 'admin':
                if st.button("🗑️ অ্যাকাউন্ট ডিলিট করুন", type="primary", use_container_width=True):
                    c.execute("DELETE FROM users WHERE username = ?", (selected_user,))
                    conn.commit()
                    st.warning(f"❌ **{selected_user}** কে ডিলিট করা হয়েছে।")
                    st.rerun()
    else:
        st.info("ℹ️ কোনো কাস্টম ইউজার অ্যাকাউন্ট পাওয়া যায়নি।")

conn.close()
