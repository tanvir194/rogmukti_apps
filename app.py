import streamlit as st
import os

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Rog Mukti Diagnostic", layout="wide")

# ২. কাস্টম সিএসএস (লগইন পেজ এবং ডার্ক থিম সুন্দর করার জন্য)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b131f !important;
        color: #e2e8f0 !important;
    }
    .stApp label {
        color: #38bdf8 !important;
        font-weight: 500 !important;
    }
    .stTextInput input {
        background-color: #18263c !important;
        color: #ffffff !important;
        border: 1px solid #2d3f5d !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    [data-testid="stSidebarNavItems"] {
        padding-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ৩. সেশন স্টেট (লগইন স্ট্যাটাস চেক)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ৪. লগইন পেজের ইন্টারফেস ফাংশন
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
            st.error("Incorrect password! Please try again.")

# ৫. মাল্টি-পেজ নেভিগেশন ও সাইডবার লজিক
if not st.session_state.logged_in:
    login_screen = st.Page(login_page, title="Admin Login", icon="🔒")
    pg = st.navigation([login_screen], position="hidden")
    pg.run()
else:
    # ফোল্ডারে ফাইলটি আছে কি না তা পরীক্ষা করে পেজ তৈরি করার নিরাপদ ফাংশন
    def create_safe_page(file_path, title, icon):
        if os.path.exists(file_path):
            return st.Page(file_path, title=title, icon=icon)
        else:
            # যদি ফাইলটি খুঁজে না পাওয়া যায়, তবে এটি ক্র্যাশ না করে একটি ডেমো পেজ তৈরি করবে
            def fallback_view():
                st.warning(f"🚨 ফাইলটি পাওয়া যায়নি: {file_path}")
                st.info("দয়া করে GitHub-এ ফাইলের নাম এবং নম্বরটি চেক করুন।")
            return st.Page(fallback_view, title=title, icon=icon)

    # আপনার স্ক্রিনশটের সব কটি পেজ নিরাপদভাবে লোড করা হচ্ছে
    patient_entry = create_safe_page("pages/1_Patient_Entry.py", "Patient Entry & Billing", "📝")
    dashboard = create_safe_page("pages/2_Dashboard.py", "Daily Dashboard", "📊")
    print_receipt = create_safe_page("pages/3_Print_Receipt.py", "Money Receipt & Print", "🖨️")
    due_collection = create_safe_page("pages/4_Due_Collection.py", "Due Collection", "💰")
    doctor_cv = create_safe_page("pages/5_Doctor_CV.py", "Doctor CV", "📄")
    doctor_referral = create_safe_page("pages/6_Doctor_Referral.py", "Doctor Referral", "🤝")
    
    # এরর দেওয়া ফাইলটিকে ৮ এবং ৯ উভয় নম্বরেই চেক করবে যেন ক্র্যাশ না করে
    admin_unlock_path = "pages/9_Admin_Unlock.py" if os.path.exists("pages/9_Admin_Unlock.py") else "pages/8_Admin_Unlock.py"
    admin_unlock = create_safe_page(admin_unlock_path, "Admin Unlock", "🔓")
    
    pathology_report = create_safe_page("pages/7_Pathology_Report.py", "Pathology Report", "🔬")
    english_receipt = create_safe_page("pages/9_English_Receipt.py", "English Receipt", "🧾")
    admin_panel = create_safe_page("pages/10_Admin_Panel.py", "Admin Panel", "⚙️")
    send_sms = create_safe_page("pages/10_Send_SMS.py", "Send SMS", "💬")
    backup_data = create_safe_page("pages/11_Backup_Data.py", "Backup Data", "💾")
    advanced_dashboard = create_safe_page("pages/12_Advanced_Dashboard.py", "Advanced Dashboard", "📈")
    logo_receipt_print = create_safe_page("pages/13_Logo_Receipt_Print.py", "Logo & Receipt Setup", "🖼️")
    
    # ক্যাটাগরি অনুযায়ী মেনু সাজানো
    pg = st.navigation({
        "প্রধান কার্যক্রম (Main)": [patient_entry, print_receipt, due_collection, english_receipt, logo_receipt_print],
        "অ্যানালিটিক্স ও রেকর্ড": [dashboard, advanced_dashboard, pathology_report],
        "যোগাযোগ ও ডাক্তার": [doctor_cv, doctor_referral, send_sms],
        "অ্যাডমিন সেকশন": [admin_unlock, admin_panel, backup_data]
    })
    
    # সাইডবারের নিচের লাইভ হিসাব
    with st.sidebar:
        st.markdown("---")
        st.subheader("🏢 Rog Mukti Diagnostic")
        st.caption("📅 তারিখ: 12 June, 2026")
        st.markdown("---")
        st.markdown("### 📊 আজকের লাইভ হিসাব")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="👥 মোট রোগী", value="0 জন")
        with col2:
            st.metric(label="💰 মোট কালেকশন", value="0 ৳")
        st.markdown("---")
        if st.button("Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.rerun()
            
    pg.run()
