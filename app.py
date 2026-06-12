import streamlit as st
import os

st.set_page_config(page_title="Rog Mukti Diagnostic", layout="wide")

# ডার্ক মোড সিএসএস
st.markdown("""
    <style>
    .stApp { background-color: #0b131f !important; color: #e2e8f0 !important; }
    .stApp label { color: #38bdf8 !important; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

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

if not st.session_state.logged_in:
    login_screen = st.Page(login_page, title="Admin Login", icon="🔒")
    pg = st.navigation([login_screen], position="hidden")
    pg.run()
else:
    # পেজগুলো লোড করার নিরাপদ সিস্টেম
    def create_safe_page(file_path, title, icon):
        if os.path.exists(file_path):
            return st.Page(file_path, title=title, icon=icon)
        else:
            def fallback(): st.warning(f"🚨 ফাইল পাওয়া যায়নি: {file_path}")
            return st.Page(fallback, title=title, icon=icon)

    patient_entry = create_safe_page("pages/1_Patient_Entry.py", "Patient Entry & Billing", "📝")
    dashboard = create_safe_page("pages/2_Dashboard.py", "Daily Dashboard", "📊")
    print_receipt = create_safe_page("pages/3_Print_Receipt.py", "Money Receipt & Print", "🖨️")
    due_collection = create_safe_page("pages/4_Due_Collection.py", "Due Collection", "💰")
    doctor_cv = create_safe_page("pages/5_Doctor_CV.py", "Doctor CV", "📄")
    doctor_referral = create_safe_page("pages/6_Doctor_Referral.py", "Doctor Referral", "🤝")
    pathology_report = create_safe_page("pages/7_Pathology_Report.py", "Pathology Report", "🔬")
    
    admin_unlock_path = "pages/9_Admin_Unlock.py" if os.path.exists("pages/9_Admin_Unlock.py") else "pages/8_Admin_Unlock.py"
    admin_unlock = create_safe_page(admin_unlock_path, "Admin Unlock", "🔓")
    
    english_receipt = create_safe_page("pages/9_English_Receipt.py", "English Receipt", "🧾")
    admin_panel = create_safe_page("pages/10_Admin_Panel.py", "Admin Panel", "⚙️")
    send_sms = create_safe_page("pages/10_Send_SMS.py", "Send SMS", "💬")
    backup_data = create_safe_page("pages/11_Backup_Data.py", "Backup Data", "💾")
    advanced_dashboard = create_safe_page("pages/12_Advanced_Dashboard.py", "Advanced Dashboard", "📈")
    logo_receipt_print = create_safe_page("pages/13_Logo_Receipt_Print.py", "Logo & Receipt Setup", "🖼️")
    
    pg = st.navigation({
        "প্রধান কার্যক্রম (Main)": [patient_entry, print_receipt, due_collection, english_receipt, logo_receipt_print],
        "অ্যানালিটিক্স ও রেকর্ড": [dashboard, advanced_dashboard, pathology_report],
        "যোগাযোগ ও ডাক্তার": [doctor_cv, doctor_referral, send_sms],
        "অ্যাডমিন সেকশন": [admin_unlock, admin_panel, backup_data]
    })
    
    with st.sidebar:
        st.markdown("### 📊 আজকের লাইভ হিসাব")
        col1, col2 = st.columns(2)
        col1.metric("👥 মোট রোগী", "0 জন")
        col2.metric("💰 মোট কালেকশন", "0 ৳")
        if st.button("Logout", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.rerun()
            
    pg.run()
