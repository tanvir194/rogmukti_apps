import streamlit as st
import sqlite3
import os

# সিকিউরিটি চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

st.title("🗂️ ডাক্তার প্রোফাইল ও সিভি ম্যানেজমেন্ট")

# সিভি সেভ করার জন্য একটি লোকাল ফোল্ডার তৈরি (যদি না থাকে)
UPLOAD_DIR = "uploaded_cvs"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# ডাটাবেজে ডাক্তার টেবিল তৈরি
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS doctor_cvs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_name TEXT,
    designation TEXT,
    phone TEXT,
    file_path TEXT
)
""")
conn.commit()

# ট্যাব সিস্টেম (১টি এন্ট্রি করার জন্য, ১টি দেখার জন্য)
tab1, tab2 = st.tabs(["➕ নতুন ডাক্তার ও সিভি যোগ করুন", "🔍 ডাক্তারদের তালিকা ও সিভি ডাউনলোড"])

# --- ট্যাব ১: ডাটা এন্ট্রি সেকশন ---
with tab1:
    st.subheader("ডাক্তারের বিস্তারিত তথ্য দিন")
    doc_name = st.text_input("ডাক্তারের নাম (Name) *")
    designation = st.text_area("পদবী ও শিক্ষাগত যোগ্যতা (Designation / Degree) *", placeholder="যেমন: এমবিবিএস, এফসিপিএস (মেডিসিন)")
    doc_phone = st.text_input("মোবাইল নম্বর (Phone)")
    
    # পিডিএফ বা ইমেজ ফাইল আপলোড অপশন
    uploaded_file = st.file_uploader("ডাক্তারের সিভি ফাইল আপলোড করুন (PDF, JPG, PNG)", type=["pdf", "jpg", "png", "jpeg"])
    
    if st.button("💾 ডাক্তারের তথ্য ও সিভি সেভ করুন", type="primary"):
        if not doc_name or not designation:
            st.error("⚠️ ডাক্তারের নাম এবং পদবী দেওয়া বাধ্যতামূলক!")
        else:
            saved_file_path = ""
            # ফাইল আপলোড হয়ে থাকলে তা লোকাল ফোল্ডারে সেভ করা
            if uploaded_file is not None:
                saved_file_path = os.path.join(UPLOAD_DIR, f"{doc_name}_{uploaded_file.name}")
                with open(saved_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            # ডাটাবেজে সেভ করা
            c.execute("""
                INSERT INTO doctor_cvs (doc_name, designation, phone, file_path)
                VALUES (?, ?, ?, ?)
            """, (doc_name, designation, doc_phone, saved_file_path))
            conn.commit()
            st.success(f"✅ {doc_name} এর প্রোফাইল ও সিভি সফলভাবে সেভ হয়েছে!")
            st.rerun()

# --- ট্যাব ২: ডাটা দেখার সেকশন ---
with tab2:
    st.subheader("নিবন্ধিত ডাক্তারদের তালিকা")
    c.execute("SELECT * FROM doctor_cvs")
    doctors = c.fetchall()
    
    if not doctors:
        st.info("ℹ️ এখনো কোনো ডাক্তারের সিভি আপলোড করা হয়নি।")
    else:
        for doc in doctors:
            # সুন্দর বক্স আকারে প্রতিটা ডাক্তারের প্রোফাইল দেখাবে
            with st.container():
                st.markdown(f"### 🩺 {doc[1]}")
                st.markdown(f"**পদবী/ডিগ্রি:** {doc[2]}")
                if doc[3]:
                    st.markdown(f"**মোবাইল:** {doc[3]}")
                
                # সিভি ফাইল ডাউনলোড বা দেখার বাটন
                file_path = doc[4]
                if file_path and os.path.exists(file_path):
                    with open(file_path, "rb") as file:
                        btn = st.download_button(
                            label="📥 সিভি (CV) ডাউনলোড করুন",
                            data=file,
                            file_name=os.path.basename(file_path),
                            mime="application/octet-stream",
                            key=f"dl_{doc[0]}"
                        )
                else:
                    st.caption("🚫 কোনো সিভি ফাইল আপলোড করা নেই।")
                st.markdown("---")

conn.close()

