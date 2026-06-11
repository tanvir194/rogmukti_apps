import streamlit as st
import pandas as pd
import sqlite3
import os

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Data Backup", layout="wide", initial_sidebar_state="expanded")

# ২. সাইডবার কালার CSS
st.markdown(
    """
    <style>
    [data-testid="stSidebarNavLink"] span {
        color: #0066CC !important; 
        font-weight: bold !important; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📥 Rog Mukti Data Backup Panel")
st.write("আপনার মোবাইল বা কম্পিউটারের লোকাল স্টোরেজে ডাটা সুরক্ষিত রাখতে এখান থেকে ফাইল ডাউনলোড করুন।")
st.markdown("---")

# ৩. ডাটাবেজ ফাইল খোঁজা
db_name = "database.db"
for file in os.listdir('.'):
    if file.endswith('.db'):
        db_name = file

try:
    # ডাটাবেজ কানেক্ট করা
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query("SELECT * FROM billing_records", conn)
    conn.close()
    
    st.success(f"📊 সফলভাবে ডাটাবেজ কানেক্ট হয়েছে! মোট {len(df)} টি রোগীর এন্ট্রি পাওয়া গেছে।")
    
    # ৪. ডাটা সিএসভি (CSV) ফরম্যাটে কনভার্ট করা (যা সরাসরি Excel-এ ওপেন হয়)
    csv_data = df.to_csv(index=False).encode('utf-8')
    
    st.markdown("### 💾 লোকাল ডিস্ক বা ফোন মেমোরিতে সেভ করুন")
    st.info("নিচের বাটনে ক্লিক করলেই ফাইলটি ডাউনলোড হয়ে সরাসরি আপনার ডিভাইস স্টোরেজে চলে যাবে।")
    
    # ৫. ডাউনলোড বাটন
    st.download_button(
        label="🟢 ডাউনলোড এক্সেল ব্যাকআপ (Excel/CSV ফরম্যাট)",
        data=csv_data,
        file_name="Rog_Mukti_Billing_Backup.csv",
        mime="text/csv"
    )
    
    # ডাটা প্রিভিউ
    st.markdown("---")
    st.subheader("📋 বর্তমান ডাটার একটি ঝলক (Preview):")
    st.dataframe(df.head(10), use_container_width=True)

except Exception as e:
    st.error("🚫 ডাটাবেজ ফাইল বা টেবিলটি এই মুহূর্তে খুঁজে পাওয়া যাচ্ছে না।")
    st.info("💡 'Patient Entry & Billing' পেজে গিয়ে অন্তত ১টি নতুন রোগীর বিল সেভ করলেই এই ব্যাকআপ পেজটি সচল হয়ে যাবে।")
