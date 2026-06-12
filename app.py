import streamlit as st

# ১. পেজ কনফিগারেশন (সবার উপরে থাকতে হবে)
st.set_page_config(page_title="Rog Mukti Diagnostic", layout="wide")

# ২. কাস্টম সিএসএস (আপনার ওয়াটারমার্ক ও সাইডবার স্টাইল অক্ষুণ্ণ রাখা হয়েছে)
st.markdown(
    """
    <style>
    [data-testid="stMainBlockContainer"], .main {
        position: relative !important;
    }
    
    [data-testid="stMainBlockContainer"]::before, .main::before {
        content: "" !important;
        position: absolute !important;
        top: 45% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        width: 320px !important;
        height: 320px !important;
        background-image: url('data:image/svg+xml;utf8,<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://w3.org"><rect x="42" y="15" width="16" height="70" fill="%23FF3366" rx="4"/><rect x="15" y="42" width="70" height="16" fill="%23FF3366" rx="4"/><path d="M 18 50 L 38 50 L 44 25 L 50 75 L 56 38 L 62 58 L 66 50 L 82 50" stroke="%23FFFFFF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M 50 5 L 85 20 L 85 55 C 85 75 50 95 50 95 C 50 95 15 75 15 55 L 15 20 Z" stroke="%230066CC" stroke-width="4" stroke-linejoin="round" fill="none"/></svg>') !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        opacity: 0.05 !important;
        pointer-events: none !important;
        z-index: 0 !important;
    }

    @media print {
        [data-testid="stSidebar"], button, header, [data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stMainBlockContainer"]::before, .main::before {
            opacity: 0.06 !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
    }
    
    /* সাইডবার মেনু হেডার এবং লেখার ডিজাইন */
    [data-testid="stSidebarNavItems"] {
        padding-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ৩. সেশন স্টেট (লগইন ট্র্যাকিং)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ৪. লগইন স্ক্রিনের জন্য একটি ফাংশন তৈরি করা
def login_page():
    st.title("🩺 Rog Mukti Diagnostic Center")
    st.subheader("🔒 Admin Login")
    
    password = st.text_input("Enter Security Password:", type="password")
    if st.button("Login", use_container_width=True):
        if password == "admin":
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Incorrect password! Please try again.")

# ৫. ডাইনামিক নেভিগেশন লজিক (লগইন অবস্থার ওপর ভিত্তি করে মেনু পরিবর্তন)
if not st.session_state.logged_in:
    # লগইন না থাকলে শুধুমাত্র লগইন পেজ দেখাবে (বাকি সব ফাইল হাইড থাকবে)
    login_screen = st.Page(login_page, title="Admin Login", icon="🔒")
    pg = st.navigation([login_screen], position="hidden") # সাইডবারে মেনু দেখাবে না লগইন ছাড়া
else:
    # লগইন থাকলে সব পেজ সুন্দর ক্যাটাগরিতে লোড হবে
    patient_entry = st.Page("pages/1_Patient_Entry.py", title="Patient Entry & Billing", icon="📝")
    dashboard = st.Page("pages/2_Dashboard.py", title="Daily Dashboard", icon="📊")
    print_receipt = st.Page("pages/3_Print_Receipt.py", title="Money Receipt & Print", icon="🖨️")
    due_collection = st.Page("pages/4_Due_Collection.py", title="Due Collection", icon="💰")
    doctor_cv = st.Page("pages/5_Doctor_CV.py", title="Doctor CV", icon="📄")
    doctor_referral = st.Page("pages/6_Doctor_Referral.py", title="Doctor Referral", icon="🤝")
    pathology_report = st.Page("pages/7_Pathology_Report.py", title="Pathology Report", icon="🔬")
    admin_unlock = st.Page("pages/8_Admin_Unlock.py", title="Admin Unlock", icon="🔓")
    english_receipt = st.Page("pages/9_English_Receipt.py", title="English Receipt", icon="🔤")
    admin_panel = st.Page("pages/10_Admin_Panel.py", title="Admin Panel", icon="⚙️")
    send_sms = st.Page("pages/10_Send_SMS.py", title="Send SMS", icon="💬")
    backup_data = st.Page("pages/11_Backup_Data.py", title="Backup Data", icon="💾")
    advanced_dashboard = st.Page("pages/12_Advanced_Dashboard.py", title="Advanced Dashboard", icon="📈")
    logo_receipt_print = st.Page("pages/13_Logo_Receipt_Print.py", title="Logo & Receipt Setup", icon="🎨")

    # গ্রুপ আকারে সাইডবার সাজানো
    pg = st.navigation({
        "প্রধান কার্যক্রম (Main)": [patient_entry, print_receipt, due_collection, english_receipt, logo_receipt_print],
        "অ্যানালিটিক্স ও রিপোর্ট": [dashboard, advanced_dashboard, pathology_report],
        "যোগাযোগ ও ডাক্তার": [doctor_cv, doctor_referral, send_sms],
        "অ্যাডমিন সেকশন": [admin_unlock, admin_panel, backup_data]
    })

    # সাইডবারের একদম নিচের দিকে লাইভ হিসাব ও লগআউট বাটন রাখা
    with st.sidebar:
        st.markdown("---")
        st.subheader("🛡️ Rog Mukti Diagnostic")
        st.caption("📅 তারিখ: 12 June, 2026")
        st.markdown("---")
        
        st.markdown("### 📊 আজকের লাইভ হিসাব")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="মোট রোগী", value="0 জন")
        with col2:
            st.metric(label="মোট কালেকশন", value="0 ৳")
        
        st.markdown("---")
        if st.button("Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.rerun()

# ৬. অ্যাপ্লিকেশন রান করা
pg.run()
