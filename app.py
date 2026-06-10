import streamlit as st

# 1. Setting the page configuration
st.set_page_config(page_title="Rog Mukti Diagnostic", layout="wide")

#2. Creating session state (login tracking)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 3. Login screen or view
if not st.session_state.logged_in:
    st.title("🏥 রোগ মুক্তি ডায়াগনস্টিক সেন্টার")
    st.subheader("🔒 অ্যাডমিন লগইন")
    
    password = st.text_input("সিকিউরিটি পাসওয়ার্ড দিন:", type="password")
    if st.button("লগইন করুন"):
        if password == "admin":
            st.session_state.logged_in = True
            st.success("লগইন সফল হয়েছে! বাম পাশের মেনু থেকে অন্য পেজে যান।")
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড! আবার চেষ্টা করুন।")
else:
    st.title("👋 স্বাগতম, অ্যাডমিন!")
    st.info("আপনার প্রজেক্টের কাজ শুরু করতে বাম পাশের সাইডবার (Sidebar) থেকে যেকোনো পেজ সিলেক্ট করুন।")
    
    # 🚨 Force navigation links (all lines are equally spaced from the beginning of the line)
    st.sidebar.markdown("### 🗂️ মেনু অপশন")
    st.sidebar.page_link("pages/1_Patient_Entry.py", label="📝 পেশেন্ট এন্ট্রি ও বিলিং", icon="📝")
    st.sidebar.page_link("pages/2_Dashboard.py", label="📊 দৈনিক ও মাসিক হিসাব", icon="📊")
    st.sidebar.page_link("pages/3_Print_Receipt.py", label="🖨️ মানি রিসিট ও প্রিন্ট", icon="🖨️")
    
    st.sidebar.markdown("---")
    # Logout button
    if st.sidebar.button("লগআউট (Logout)"):
        st.session_state.logged_in = False
        st.rerun()
        
