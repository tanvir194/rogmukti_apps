import streamlit as st
import pandas as pd
import sqlite3
import os

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Logo Receipt Print", layout="wide", initial_sidebar_state="expanded")

# ২. প্রিন্ট সিএসএস, সাইডবার কালার এবং জাদুকরী জলছাপ (Watermark) লজিক
st.markdown(
    """
    <style>
    [data-testid="stSidebarNavLink"] span {
        color: #0066CC !important; 
        font-weight: bold !important; 
    }
    
    /* 🛡️ রিসিট বক্সের ভেতরে জলছাপ বা ওয়াটারমার্ক যুক্ত করার স্পেশাল ডিজাইন */
    .receipt-container {
        position: relative;
        background-color: #FFFFFF !important;
        padding: 20px;
        border: 1px solid #DDDDDD;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* জলছাপের লোগো ইমেজের পজিশন ও ঝাপসা (Opacity) করার লজিক */
    .receipt-container::before {
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 250px; /* জলছাপের সাইজ */
        height: 250px;
        /* আপনার নির্দিষ্ট মেডিকেল শিল্ড লোগোর লাইট সংস্করণ জলছাপ হিসেবে ব্যবহার করা হলো */
        background-image: url('data:image/svg+xml;utf8,<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://w3.org"><rect x="42" y="15" width="16" height="70" fill="%23FF3366" rx="4"/><rect x="15" y="42" width="70" height="16" fill="%23FF3366" rx="4"/><path d="M 18 50 L 38 50 L 44 25 L 50 75 L 56 38 L 62 58 L 66 50 L 82 50" stroke="%23FFFFFF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M 50 5 L 85 20 L 85 55 C 85 75 50 95 50 95 C 50 95 15 75 15 55 L 15 20 Z" stroke="%230066CC" stroke-width="4" stroke-linejoin="round" fill="none"/></svg>');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        opacity: 0.08; /* মাত্র ৮% ঝাপসা রাখা হলো যাতে লেখার ব্যাকগ্রাউন্ডে হালকা জলছাপ দেখায় */
        pointer-events: none;
        z-index: 0;
    }
    
    /* রিসিটের ভেতরের কন্টেন্টগুলো যেন জলছাপের ওপরে স্পষ্ট থাকে */
    .receipt-content {
        position: relative;
        z-index: 1;
    }
    
    @media print {
        [data-testid="stSidebar"], button, header, [data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stMainBlockContainer"] {
            padding: 0 !important;
            margin: 0 auto !important;
            width: 100% !important;
        }
        /* প্রিন্ট করার সময়ও জলছাপ যেন হালকাভাবে কাগজে দৃশ্যমান থাকে */
        .receipt-container::before {
            opacity: 0.08 !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🖨️ লোগো ও জলছাপসহ রিসিট প্রিন্ট প্যানেল")
st.write("আপনার ডায়াগনস্টিক সেন্টারের নির্দিষ্ট লোগো এবং হালকা জলছাপসহ যেকোনো রিসিট প্রিন্ট করতে নিচে বিল নম্বর দিন।")
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
        bill_col = df_bill.columns
        p_data = df_bill[df_bill[bill_col].astype(str) == str(bill_no_input).strip()]
        conn.close()
        
        if not p_data.empty:
            patient = p_data.iloc[0]
            
            st.markdown("### 📋 প্রিন্ট প্রিভিউ (Print Preview):")
            
            # এইচটিএমএল ডিভ ব্যবহার করে জলছাপের কন্টেইনার তৈরি করা হলো
            st.markdown('<div class="receipt-container"><div class="receipt-content">', unsafe_allow_html=True)
            
            # টপ লোগো সেকশন
            st.markdown(
                """
                <div style="text-align: center; margin-bottom: 5px;">
                    <svg width="70" height="70" viewBox="0 0 100 100" xmlns="http://w3.org">
                        <rect x="42" y="15" width="16" height="70" fill="#FF3366" rx="4"/>
                        <rect x="15" y="42" width="70" height="16" fill="#FF3366" rx="4"/>
                        <path d="M 18 50 L 38 50 L 44 25 L 50 75 L 56 38 L 62 58 L 66 50 L 82 50" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                        <path d="M 50 5 L 85 20 L 85 55 C 85 75 50 95 50 95 C 50 95 15 75 15 55 L 15 20 Z" stroke="#0066CC" stroke-width="4" stroke-linejoin="round" fill="none"/>
                    </svg>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.markdown("<h2 style='text-align: center; color: #0066CC; margin-top:5px; margin-bottom: 2px;'>রোগ মুক্তি ডায়াগনস্টিক সেন্টার</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; margin-top:0px; font-weight: bold; color: gray;'>গলাচিপা, পটুয়াখালী | হেল্পলাইন: ০১৭XXXXXXXX</p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            col1.write(f"**বিল নম্বর (Bill No):** {patient[bill_col]}")
            col1.write(f"**রোগীর নাম (Patient Name):** {patient.get('patient_name', 'N/A')}")
            col1.write(f"**মোবাইল নম্বর (Phone):** {patient.get('phone', 'N/A')}")
            
            col2.write(f"**তারিখ (Date):** {str(patient.get('date', 'N/A'))[:10]}")
            col2.write(f"**বয়স (Age):** {patient.get('age', 'N/A')}")
            col2.write(f"**রেফার্ড ডাক্তার (Refd By):** {patient.get('ref_by', 'N/A')}")
            
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            st.write(f"🔬 **সিলেক্ট করা টেস্ট সমূহ (Tests Requested):**")
            st.info(f"👉 {patient.get('tests', 'N/A')}")
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            
            col_m1, col_m2 = st.columns(2)
            with col_m2:
                st.write(f"**মোট বিল (Total Amount):** {patient.get('total_amount', 0.0)} ৳")
                st.write(f"**ডিসকাউন্ট (Discount):** {patient.get('discount', 0.0)} ৳")
                st.write(f"**অগ্রিম পরিশোধ (Advance Paid):** {patient.get('advance', 0.0)} ৳")
                st.markdown("---")
                st.write(f"### 🔴 বাকি টাকা (Due Amount): {patient.get('due_amount', 0.0)} ৳")
            
            st.markdown("<br><p style='text-align: center; font-size: 12px; color: gray;'>রিসিটটি তৈরি করার জন্য ধন্যবাদ। সুস্থ থাকুন।</p>", unsafe_allow_html=True)
            
            # কন্টেইনার ক্লোজ করা হলো
            st.markdown('</div></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.write("💡 **প্রিন্ট করার নিয়ম:** নিচের বাটনে ক্লিক করলে আপনার প্রিন্ট উইন্ডো চালু হবে।")
            
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
