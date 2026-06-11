import streamlit as st
import pandas as pd
import sqlite3
import io

# ১. পেজ কনফিগারেশন ও সাইডবার অটো-ওপেন
st.set_page_config(page_title="Data Backup & Download", layout="wide", initial_sidebar_state="expanded")

# ২. সাইডবার মেনু কালারিং CSS
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

# ৩. ডাটাবেজ থেকে লাইভ ডাটা রিড করা
try:
    # আপনার প্রজেক্টের ডাটাবেজ ফাইলের নাম যদি অন্য হয় (যেমন: database.db), তবে নিচে 'rogmukti.db' পরিবর্তন করে তা লিখুন
    conn = sqlite3.connect("rogmukti.db") 
    
    # billing_records টেবিলের সব ডাটা এক্সেল করার জন্য তুলে আনা
    query = "SELECT * FROM billing_records"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    st.success(f"📊 সফলভাবে ডাটাবেজ কানেক্ট হয়েছে! মোট {len(df)} টি রোগীর এন্ট্রি পাওয়া গেছে।")
    
    # ৪. ডাটাবেজকে Excel ফাইলে কনভার্ট করার ম্যাজিক লজিক
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Billing Records')
    
    buffer.seek(0)
    
    st.markdown("### 💾 লোকাল ডিস্ক বা ফোন মেমোরিতে সেভ করুন")
    st.info("নিচের বাটনে ক্লিক করলেই ফাইলটি ডাউনলোড হয়ে সরাসরি আপনার ডিভাইস স্টোরেজে চলে যাবে।")
    
    # ৫. ১-ক্লিক ডাউনলোড বাটন
    st.download_button(
        label="🟢 ডাউনলোড এক্সেল ব্যাকআপ (Excel .xlsx)",
        data=buffer,
        file_name="Rog_Mukti_Billing_Backup.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # লাইভ ডাটা প্রিভিউ
    st.markdown("---")
    st.subheader("📋 বর্তমান ডাটার একটি ঝলক (Preview):")
    st.dataframe(df.head(10), use_container_width=True)

except Exception as e:
    st.error("🚫 ডাটাবেজ ফাইল বা টেবিলটি এই মুহূর্তে খুঁজে পাওয়া যাচ্ছে না।")
    st.info("💡 ড্যাশবোর্ডের এররের মতোই, 'Patient Entry & Billing' পেজে গিয়ে অন্তত ১টি নতুন রোগীর বিল সেভ করলেই এই ব্যাকআপ পেজটি সচল হয়ে যাবে।")
  
