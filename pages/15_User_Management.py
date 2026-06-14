import streamlit as st
import sqlite3

# --- ডাটাবেজ কানেকশন ---
# আপনার প্রজেক্টের ডাটাবেজ ফাইলের নাম অনুযায়ী কানেক্ট করা হলো
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()

# ইউজার টেবিল তৈরি (না থাকলে অটো তৈরি হবে)
c.execute("""CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY, 
    password TEXT,
    role TEXT DEFAULT 'staff')""")

# প্রথমবার রান করার জন্য একটি ডিফল্ট অ্যাডমিন অ্যাকাউন্ট তৈরি রাখা হলো
c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")
conn.commit()

# --- পেজ ডিজাইন ---
st.set_page_config(page_title="ইউজার কন্ট্রোল প্যানেল", page_icon="🔐", layout="centered")

st.title("🔐 স্টাফ ও পাসওয়ার্ড কন্ট্রোল প্যানেল")
st.write("এখান থেকে নতুন স্টাফ যোগ করতে পারবেন এবং সবার পাসওয়ার্ড পরিবর্তন বা মডিফাই করতে পারবেন।")
st.markdown("---")

# দুটি আলাদা কাজের জন্য ট্যাব সিস্টেম
tab1, tab2 = st.tabs(["➕ নতুন স্টাফ যোগ করুন", "🔄 পাসওয়ার্ড পরিবর্তন ও মডিফাই"])

# ট্যাব ১: নতুন স্টাফ অ্যাকাউন্ট তৈরি
with tab1:
    st.subheader("নতুন স্টাফ অ্যাকাউন্ট রেজিস্টার")
    new_user = st.text_input("নতুন ইউজারনেম (Username)", key="new_username_input")
    new_pass = st.text_input("পাসওয়ার্ড (Password)", type="password", key="new_password_input")
    user_role = st.selectbox("ব্যবহারকারীর রোল/পদবী", ["staff", "admin"], key="user_role_select")
    
    if st.button("➕ স্টাফ অ্যাকাউন্ট তৈরি করুন", use_container_width=True):
        if new_user and new_pass:
            try:
                # ইউজারনেমের দুই পাশের স্পেস কেটে সেভ করা হচ্ছে
                c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (new_user.strip(), new_pass, user_role))
                conn.commit()
                st.success(f"🎉 সফলতা! **{new_user.strip()}** এর অ্যাকাউন্ট তৈরি হয়েছে।")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("❌ এই ইউজারনেমটি ইতিমধ্যে সিস্টেমে ব্যবহার করা হয়েছে! অন্য নাম দিন।")
        else:
            st.error("⚠️ দয়া করে ইউজারনেম এবং পাসওয়ার্ড দুটি ঘরই পূরণ করুন।")

# 🖥️ ট্যাব ২: পাসওয়ার্ড আপডেট এবং ইউজার ডিলিট করা
with tab2:
    st.subheader("বর্তমান ইউজারদের পাসওয়ার্ড পরিবর্তন")
    
    # ডাটাবেজ থেকে সব ইউজারের তালিকা নিয়ে আসা
    c.execute("SELECT username FROM users")
    all_users = [row[0] for row in c.fetchall()]
    
    if all_users:
        selected_user = st.selectbox("কোন ইউজারের পাসওয়ার্ড মডিফাই করবেন?", all_users, key="select_user_to_modify")
        updated_pass = st.text_input("নতুন পাসওয়ার্ড দিন", type="password", key="update_password_input")
        
        st.write("") # একটু ফাঁকা জায়গা তৈরি করার জন্য
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 পাসওয়ার্ড আপডেট করুন", use_container_width=True):
                if updated_pass:
                    c.execute("UPDATE users SET password = ? WHERE username = ?", (updated_pass, selected_user))
                    conn.commit()
                    st.success(f"✅ **{selected_user}** এর নতুন পাসওয়ার্ড সফলভাবে আপডেট হয়েছে!")
                else:
                    st.error("⚠️ নতুন পাসওয়ার্ডের ঘরটি খালি রাখা যাবে না।")
                    
        with col2:
            # সুরক্ষার জন্য মেইন 'admin' অ্যাকাউন্টটি যেন ডিলিট না হয়ে যায় তা লক করা হলো
            if selected_user != 'admin':
                if st.button("🗑️ অ্যাকাউন্ট ডিলিট করুন", type="primary", use_container_width=True):
                    c.execute("DELETE FROM users WHERE username = ?", (selected_user,))
                    conn.commit()
                    st.warning(f"❌ **{selected_user}** কে সিস্টেম থেকে ডিলিট করা হয়েছে।")
                    st.rerun()
            else:
                st.info("ℹ️ মূল 'admin' অ্যাকাউন্টটি ডিলিট করা যাবে his।")
    else:
        st.info("কোনো ইউজার অ্যাকাউন্ট পাওয়া যায়নি।")

# ডাটাবেজ কানেকশন বন্ধ করা
conn.close()
                  
