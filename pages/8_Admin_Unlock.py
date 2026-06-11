import streamlit as st

# ১. পেজ কনফিগারেশন এবং সাইডবার অটো-ওপেন রাখা
st.set_page_config(page_title="Admin Master Unlock", layout="wide", initial_sidebar_state="expanded")

# ২. লগইন ট্র্যাকিং সেশন তৈরি
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ৩. সাইডবার মেনু এবং কালারিং CSS
st.markdown(
    """
    <style>
    [data-testid="stSidebarNavLink"] span {
        color: #0066CC !important; 
        font-weight: bold !important; 
        font-size: 15px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ৪. মাস্টার কন্ট্রোল লজিক
st.title("🔒 Rog Mukti Admin Master Control")
st.markdown("---")

if st.session_state.logged_in:
    st.success("🔓 অ্যাপটি বর্তমানে সম্পূর্ণ আনলকড! আপনার সমস্ত কাস্টম মেনু বাম পাশের সাইডবারে সচল হয়েছে।")
    st.info("💡 এখন আপনি বাম পাশের সাইডবার থেকে যেকোনো পেজে প্রবেশ করতে পারবেন।")
    
    # লগআউট বাটন (যা আবার সবকিছু লক করে দেবে)
    if st.button("🔴 অ্যাপটি পুনরায় লক করুন (Logout)"):
        st.session_state.logged_in = False
        st.rerun()
else:
    st.subheader("🔑 সিকিউরিটি ভেরিফিকেশন")
    st.write("রোগী এন্ট্রি ছাড়া বাকি সমস্ত প্যানেল কন্ট্রোল করতে এখানে পাসওয়ার্ড দিন:")
    
    password = st.text_input("পাসওয়ার্ড লিখুন:", type="password")
    
    if st.button("আনলক করুন"):
        if password == "admin": # আপনার আসল পাসওয়ার্ড এখানে দিতে পারেন
            st.session_state.logged_in = True
            st.success("🔓 সফলভাবে আনলক হয়েছে! পেজটি রিফ্রেশ হচ্ছে...")
            st.rerun()
        else:
            st.error("❌ ভুল পাসওয়ার্ড! সঠিক পাসওয়ার্ড দিয়ে আবার চেষ্টা করুন।")

# ৫. ডাইনামিক সাইডবার নেভিগেশন (যা সব পেজকে নিয়ন্ত্রণ করছে)
st.sidebar.markdown("### 🗂️ Menu Options")

# এই পেজটি লক ছাড়া সবসময় সবাই দেখতে পাবে (আপনার রিকোয়ারমেন্ট অনুযায়ী)
st.sidebar.page_link("pages/1_Patient_Entry.py", label="Patient Entry & Billing", icon="📝")

# 🔒 যদি অ্যাডমিন লগইন করে, তবেই বাকি পেজগুলোর লিংক সাইডবারে ভেসে উঠবে
if st.session_state.logged_in:
    st.sidebar.markdown("---")
    st.sidebar.markdown("⚙️ **Admin Locked Pages:**")
    st.sidebar.page_link("pages/2_Dashboard.py", label="Daily & Monthly Dashboard", icon="📊")
    st.sidebar.page_link("pages/3_Print_Receipt.py", label="Money Receipt & Print", icon="🖨️")
    st.sidebar.page_link("pages/4_Due_Collection.py", label="Due Collection", icon="💰")
    st.sidebar.page_link("pages/5_Doctor_CV.py", label="Doctor CV", icon="📄")
    st.sidebar.page_link("pages/6_Doctor_Referral.py", label="Doctor Referral & Commission", icon="🩺")
    st.sidebar.page_link("pages/7_Pathology_Report.py", label="Pathology Report", icon="🔬")
    st.sidebar.page_link("pages/9_English_Receipt.py", label="English Receipt", icon="📝")
    st.sidebar.page_link("pages/10_Send_SMS.py", label="Send SMS", icon="💬")
