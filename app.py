import streamlit as st
import datetime

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Rog Mukti Diagnostic", layout="wide")

# 🛡️ এটি আপনার অ্যাপের সব পেজে প্রিন্ট করার সময় লোগো ও জলছাপ অটো-ইনজেক্ট করবে
st.markdown(
    """
    <style>
    /* ১. স্ক্রিন এবং প্রিন্ট উভয় জায়গাতেই জলছাপ বসানোর মেইন লজিক */
    [data-testid="stMainBlockContainer"], .main {
        position: relative !important;
    }
    
    [data-testid="stMainBlockContainer"]::before, .main::before {
        content: "" !important;
        position: absolute !important;
        top: 45% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        width: 320px !important; /* জলছাপের সাইজ */
        height: 320px !important;
        /* রোগ মুক্তি ডায়াগনস্টিক সেন্টারের নির্দিষ্ট লোগো (শিল্ড + প্লাস + হার্টবিট) */
        background-image: url('data:image/svg+xml;utf8,<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://w3.org"><rect x="42" y="15" width="16" height="70" fill="%23FF3366" rx="4"/><rect x="15" y="42" width="70" height="16" fill="%23FF3366" rx="4"/><path d="M 18 50 L 38 50 L 44 25 L 50 75 L 56 38 L 62 58 L 66 50 L 82 50" stroke="%23FFFFFF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M 50 5 L 85 20 L 85 55 C 85 75 50 95 50 95 C 50 95 15 75 15 55 L 15 20 Z" stroke="%230066CC" stroke-width="4" stroke-linejoin="round" fill="none"/></svg>') !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        opacity: 0.05 !important; /* হালকা ঝাপসা থাকবে যাতে মেমোর লেখা পরিষ্কার পড়া যায় */
        pointer-events: none !important;
        z-index: 0 !important;
    }

    /* ২. প্রিন্ট করার সময় ব্রাউজার যেন জলছাপটি বাধ্যতামূলক কাগজে দেখায় */
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
    
    /* ৩. সাইডবারের অপশনগুলোর লেখার কালার কাস্টমাইজেশন */
    [data-testid="stSidebarNavLink"] span {
        color: #0066CC !important; /* সুন্দর নীল কালার */
        font-weight: bold !important;
        font-size: 15px !important;
    }
    [data-testid="stSidebarNavLink"]:hover span {
        color: #FF3366 !important; /* মাউস হোভার করলে লালচে কালার */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ২. Creating session state (login tracking)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ৩. Login screen or view
if not st.session_state.logged_in:
    st.title("🩺 Rog Mukti Diagnostic Center")
    st.subheader("🔒 Admin Login")
    
    password = st.text_input("Enter Security Password:", type="password")
    if st.button("Login"):
        if password == "admin":
            st.session_state.logged_in = True
            st.success("Login successful! Please select a page from the sidebar menu.")
            st.rerun()
        else:
            st.error("Incorrect password! Please try again.")
else:
    st.title("👋 Welcome, Admin!")
    st.info("To start working on your project, select any page from the sidebar menu.")
    
    # Force navigation links
    st.sidebar.markdown("### 🗂️ Menu Options")
    st.sidebar.page_link("pages/1_Patient_Entry.py", label="Patient Entry & Billing", icon="📝")
    st.sidebar.page_link("pages/2_Dashboard.py", label="Daily & Monthly Dashboard", icon="📊")
    st.sidebar.page_link("pages/3_Print_Receipt.py", label="Money Receipt & Print", icon="🖨️")
    
    st.sidebar.markdown("---")
    # Logout Button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
