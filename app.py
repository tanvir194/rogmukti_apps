import streamlit as st

# ১. পেজ কনফিগারেশন (সবার উপরে থাকবে)
st.set_page_config(page_title="Rog Mukti Diagnostic", layout="wide")

# ২. কাস্টম সিএসএস (লগইন পেজ এবং ডার্ক থিম সুন্দর করার জন্য)
st.markdown("""
    <style>
    /* মূল অ্যাপ ব্যাকগ্রাউন্ড ও লেখা */
    .stApp {
        background-color: #0b131f !important;
        color: #e2e8f0 !important;
    }
    
    /* লেবেল বা লেখার শিরোনামের কালার */
    .stApp label {
        color: #38bdf8 !important;
        font-weight: 500 !important;
    }
    
    /* লগইন ইনপুট বক্স ডিজাইন */
    .stTextInput input {
        background-color: #18263c !important;
        color: #ffffff !important;
        border: 1px solid #2d3f5d !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    /* ব্যাকগ্রাউন্ড লোগো বা ওয়াটারমার্ক ইফেক্ট */
    [data-testid="stMainBlockContainer"]::before {
        content: "" !important;
        position: absolute !important;
        top: 45% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        width: 320px !important;
        height: 320px !important;
        background-image: url('data:image/svg+xml;utf8,<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://w3.org"><circle cx="50" cy="50" r="40" fill="none" stroke="%2338bdf8" stroke-width="2"/></svg>') !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        opacity: 0.05 !important;
        pointer-events: none !important;
        z-index: 0 !important;
    }
    
    /* প্রিন্ট মোড সেটিংস */
    @media print {
        [data-testid="stSidebar"], button, header, [data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stMainBlockContainer"]::before {
            opacity: 0.05 !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
    }
    
    /* সাইডbar আইটেম স্পেসিং */
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
    # আপনার স্ক্রিনশটের সব কটি পেজের নাম ও আইকন হুবহু লোড করা হলো
    patient_entry = st.Page("pages/1_Patient_Entry.py", title="Patient Entry & Billing", icon="📝")
    dashboard = st.Page("pages/2_Dashboard.py", title="Daily Dashboard", icon="📊")
    print_receipt = st.Page("pages/3_Print_Receipt.py", title="Money Receipt & Print", icon="🖨️")
    due_collection = st.Page("pages/4_Due_Collection.py", title="Due Collection", icon="💰")
    doctor_cv = st.Page("pages/5_Doctor_CV.py", title="Doctor CV", icon="📄")
    doctor_referral = st.Page("pages/6_Doctor_Referral.py", title="Doctor Referral", icon="🤝")
    pathology_report = st.Page("pages/7_Pathology_Report.py", title="Pathology Report", icon="🔬")
    admin_unlock = st.Page("pages/9_Admin_Unlock.py", title="Admin Unlock", icon="🔓")
    english_receipt = st.Page("pages/9_English_Receipt.py", title="English Receipt", icon="🧾")
    admin_panel = st.Page("pages/10_Admin_Panel.py", title="Admin Panel", icon="⚙️")
    send_sms = st.Page("pages/10_Send_SMS.py", title="Send SMS", icon="💬")
    backup_data = st.Page("pages/11_Backup_Data.py", title="Backup Data", icon="💾")
    advanced_dashboard = st.Page("pages/12_Advanced_Dashboard.py", title="Advanced Dashboard", icon="📈")
    logo_receipt_print = st.Page("pages/13_Logo_Receipt_Print.py", title="Logo & Receipt Setup", icon="🖼️")
    
    # ক্যাটাগরি অনুযায়ী সাজানো (আপনার ২য় স্ক্রিনশটের ডিকশনারি অনুযায়ী)
    pg = st.navigation({
        "প্রধান কার্যক্রম (Main)": [patient_entry, print_receipt, due_collection, english_receipt, logo_receipt_print],
        "অ্যানালিটিক্স ও রেকর্ড": [dashboard, advanced_dashboard, pathology_report],
        "যোগাযোগ ও ডাক্তার": [doctor_cv, doctor_referral, send_sms],
        "অ্যাডমিন সেকশন": [admin_unlock, admin_panel, backup_data]
    })
    
    # সাইডবারের নিচের লাইভ হিসাবের প্যানেল (আপনার স্ক্রিনশটের হুবহু কোড)
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
