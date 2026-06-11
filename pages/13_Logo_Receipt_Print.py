import streamlit as st
import pandas as pd
import sqlite3
import os

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Logo Receipt Print", layout="wide", initial_sidebar_state="expanded")

# ২. প্রিন্ট করার সময় লোগো এবং রিসিট যেন নিখুঁত আসে তার জন্য CSS
st.markdown(
    """
    <style>
    /* সাইডবার মেনু কালার */
    [data-testid="stSidebarNavLink"] span {
        color: #0066CC !important; 
        font-weight: bold !important; 
    }
    
    /* 🖨️ প্রিন্ট করার স্পেশাল সেটিংস */
    @media print {
        /* প্রিন্ট করার সময় সাইডবার এবং ব্রাউজারের অন্য বাটন লুকিয়ে ফেলা */
        [data-testid="stSidebar"], button, header, [data-testid="stHeader"] {
            display: none !important;
        }
        /* মূল রিসিটের অংশটি স্ক্রিনের মাঝখানে আনা */
        [data-testid="stMainBlockContainer"] {
            padding: 0 !important;
            margin: 0 auto !important;
            width: 100% !important;
        }
        /* লোগো ইমেজ যেন প্রিন্টে পরিষ্কার আসে */
        img {
            visibility: visible !important;
            display: block !important;
            margin: 0 auto 10px auto !important;
            max-width: 150px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🖨️ লোগোসহ রিসিট প্রিন্ট প্যানেল")
st.write("আপনার ডায়াগনস্টিক সেন্টারের লোগোসহ যেকোনো রিসিট প্রিন্ট করতে নিচে বিল নম্বর দিন।")
st.markdown("---")

# ৩. ডাটাবেজ ফাইল অটো-ডিটেক্ট করা
db_name = "database.db"
for file in os.listdir('.'):
    if file.endswith('.db'):
        db_name = file

table_name = "billing_records"
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

# ৪. বিল নম্বর ইনপুট বক্স
bill_no_input = st.text_input("🧾 রিসিট প্রিন্ট করার জন্য বিল নম্বর (Bill No) লিখুন:", placeholder="যেমন: 1, 2, 3...")

if bill_no_input:
    try:
        conn = sqlite3.connect(db_name)
        df_bill = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        bill_col = df_bill.columns[0] # প্রথম কলামকে বিল নং ধরা হলো
        
        # নির্দিষ্ট বিলের ডাটা ফিল্টার করা
        p_data = df_bill[df_bill[bill_col].astype(str) == str(bill_no_input).strip()]
        conn.close()
        
        if not p_data.empty:
            patient = p_data.iloc[0]
            
            # ================= 📦 লাইভ রিসিট বক্স ডিজাইন =================
            st.markdown("### 📋 প্রিন্ট প্রিভিউ (Print Preview):")
            
            with st.container(border=True):
                # 🔴 লোগো সেকশন (এখানে আপনার ডায়াগনস্টিক সেন্টারের লোগোর অনলাইন লিংক বসাবেন)
                # আপাতত একটি ডেমো মেডিকেল লোগোর লিংক দেওয়া আছে, আপনার আসল লোগোর লিংক এখানে পেস্ট করে দেবেন
                logo_url = "https://flaticon.com"
                st.image(logo_url, width=120)
                
                st.markdown("<h2 style='text-align: center; color: #0066CC; margin-top:0;'>রোগ মুক্তি ডায়াগনস্টিক সেন্টার</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; margin-top:-10px;'>গলাচিপা, পটুয়াখালী | হেল্পলাইন: ০১৭XXXXXXXX</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                
                # রোগীর তথ্য সাজানো
                col1, col2 = st.columns(2)
                col1.write(f"**বিল নম্বর (Bill No):** {patient[bill_col]}")
                col1.write(f"**রোগীর নাম (Patient Name):** {patient.get('patient_name', patient.iloc[1])}")
                col1.write(f"**মোবাইল নম্বর (Phone):** {patient.get('phone', 'N/A')}")
                
                col2.write(f"**তারিখ (Date):** {str(patient.get('date', 'N/A'))[:10]}")
                col2.write(f"**বয়স (Age):** {patient.get('age', 'N/A')}")
                col2.write(f"**রেফার্ড ডাক্তার (Refd By):** {patient.get('ref_by', 'N/A')}")
                
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                
                # টেস্টের তালিকা
                st.write(f"🔬 **সিলেক্ট করা টেস্ট সমূহ (Tests Requested):**")
                st.info(f"👉 {patient.get('tests', 'N/A')}")
                
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                
                # টাকার হিসাব চার্ট
                col_m1, col_m2 = st.columns(2)
                with col_m2:
                    st.write(f"**মোট বিল (Total Amount):** {patient.get('total_amount', 0.0)} ৳")
                    st.write(f"**ডিসকাউন্ট (Discount):** {patient.get('discount', 0.0)} ৳")
                    st.write(f"**অগ্রিম পরিশোধ (Advance Paid):** {patient.get('advance', 0.0)} ৳")
                    st.markdown("---")
                    st.write(f"### 🔴 বাকি টাকা (Due Amount): {patient.get('due_amount', 0.0)} ৳")
                
                st.markdown("<br><p style='text-align: center; font-size: 12px; color: gray;'>রিসিটটি তৈরি করার জন্য ধন্যবাদ। সুস্থ থাকুন।</p>", unsafe_allow_html=True)
            
            # 🖨️ প্রিন্ট করার বোতাম
            st.markdown("---")
            st.write("💡 **প্রিন্ট করার নিয়ম:** নিচের বাটনে ক্লিক করলে আপনার মোবাইল বা কম্পিউটারের প্রিন্ট উইন্ডো চালু হবে। সেখানে 'Print' চাপলেই লোগোসহ মেমো বের হয়ে আসবে।")
            
            # জাভাস্ক্রিপ্ট প্রিন্ট বাটন লজিক
            st.button("🖨️ রিসিটটি এখনই প্রিন্ট করুন", on_click=st.write, args=("",), key="print_js_btn")
            st.markdown("""
                <script>
                const printBtn = window.parent.document.querySelector('button[key="print_js_btn"]');
                if (printBtn) {
                    printBtn.addEventListener('click', () => { window.print(); });
                }
                </script>
            """, unsafe_allow_html=True)

        else:
            st.error(f"❌ বিল নম্বর '{bill_no_input}' এর কোনো রেকর্ড ডাটাবেজে খুঁজে পাওয়া যায়নি!")
    except Exception as e:
        st.error(f"ডাটাবেজ থেকে বিল লোড করতে সমস্যা হয়েছে: {e}")
