import streamlit as st

# 1. Setting the page configuration
st.set_page_config(page_title="Rog Mukti Diagnostic", layout="wide")

# 2. Creating session state (login tracking)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 3. Login screen or view
if not st.session_state.logged_in:
    st.title("🏥 Rog Mukti Diagnostic Center")
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
    
    # 🚨 Force navigation links (all lines are equally spaced from the beginning of the line)
    st.sidebar.markdown("### 🗂️ Menu Options")
    st.sidebar.page_link("pages/1_Patient_Entry.py", label="📝 Patient Entry & Billing", icon="📝")
    st.sidebar.page_link("pages/2_Dashboard.py", label="📊 Daily & Monthly Dashboard", icon="📊")
    st.sidebar.page_link("pages/3_Print_Receipt.py", label="🖨️ Money Receipt & Print", icon="🖨️")
    
    st.sidebar.markdown("---")
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

