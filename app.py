import streamlit as st
import os

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Rog Mukti Diagnostic", layout="wide")

# ২. ডার্ক থিম সিএসএস
st.markdown("""
    <style>
    .stApp { background-color: #0b131f !important; color: #e2e8f0 !important; }
    .stApp label { color: #38bdf8 !important; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# ৩. সেশন স্টেট চেক
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ৪. লগইন পেজ ফাংশন
def login_page():
    st.title("🏢 Rog Mukti Diagnostic Center")
    st.subheader("🔒 Admin Login")
    password = st.text_input("Enter Security Password", type="password")
    if st.button("Login", use_container_width=True):
        if password == "admin":
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Incorrect password!")

# ৫. নেভিগেশন ও সাইডবার লজিক
if not st.session_state.logged_in:
    login_screen = st.Page(login_page, title="Admin Login", icon="🔒")
    pg = st.navigation([login_screen], position="hidden")
    pg.run()
else:
    # পেজগুলো লোড করার নিরাপদ সিস্টেম
    def safe_p(path, name, ico):
        if os.path.exists(path):
            return st.Page(path, title=name, icon=ico)
        else:
            def fb(): st.warning(f"🚨 ফাইল পাওয়া যায়নি: {path}")
            return st.Page(fb, title=name, icon=ico)

    # আপনার সবগুলো পেজের সরল তালিকা
    p1 = safe_p("pages/1_Patient_Entry.py", "Patient Entry & Billing", "📝")
    p2 = safe_p("pages/2_Dashboard.py", "Daily Dashboard", "📊")
    p3 = safe_p("pages/3_Print_Receipt.py", "Money Receipt & Print", "🖨️")
    p4 = safe_p("pages/4_Due_Collection.py", "Due Collection", "💰")
    p5 = safe_p("pages/5_Doctor_CV.py", "Doctor CV", "📄")
    p6 = safe_p("pages/6_Doctor_Referral.py", "Doctor Referral", "🤝")
    p7 = safe_p("pages/7_Pathology_Report.py", "Pathology Report", "🔬")
    p8 = safe_p("pages/9_Admin_Unlock.py", "Admin Unlock", "🔓") if os.path.exists("pages/9_Admin_Unlock.py") else safe_p("pages/8_Admin_Unlock.py", "Admin Unlock", "🔓")
    p9 = safe_p("pages/9_English_Receipt.py", "English Receipt", "🧾")
    p10 = safe_p("pages/10_Admin_Panel.py", "Admin Panel", "⚙️")
    p11 = safe_p("pages/10_Send_SMS.py", "Send SMS", "💬")
    p12 = safe_p("pages/11_Backup_Data.py", "Backup Data", "💾")
    p13 = safe_p("pages/12_Advanced_Dashboard.py", "Advanced Dashboard", "📈")
    p14 = safe_p("pages/13_Logo_Receipt_Print.py", "Logo & Receipt Setup", "🖼️")
    
    # মেনু নেভিগেশন রান করা
    pg = st.navigation({
        "প্রধান কার্যক্রম (Main)": [p1, p3, p4, p9, p14],
        "অ্যানালিটিক্স ও রেকর্ড": [p2, p13, p7],
        "যোগাযোগ ও ডাক্তার": [p5, p6, p11],
        "অ্যাডমিন সেকশন": [p8, p10, p12]
    })
    
    # সাইডবার প্যানেল
    with st.sidebar:
        st.markdown("### 📊 আজকের লাইভ হিসাব")
        col1, col2 = st.columns(2)
        col1.metric("👥 মোট রোগী", "0 জন")
        col2.metric("💰 মোট কালেকশন", "0 ৳")
        if st.button("Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.rerun()
            
    pg.run()
