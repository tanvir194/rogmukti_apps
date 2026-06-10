import streamlit as st

st.title("🔑 অ্যাডমিন প্যানেল আনলকার")
st.write("---")

# সিকিউরিটি পাসওয়ার্ড সেট করুন (এখানে আপনি আপনার পছন্দমতো পাসওয়ার্ড দিতে পারেন)
ADMIN_PASSWORD = "rogmukti_admin"

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if st.session_state.admin_authenticated:
    st.success("✅ সমস্ত গোপন ফিচার এখন আনলক করা আছে!")
    if st.button("🔒 আবার লক করুন (Lock Pages)"):
        st.session_state.admin_authenticated = False
        st.rerun()
else:
    password_input = st.text_input("অ্যাডমিন পাসওয়ার্ড দিন (Enter Password):", type="password")
    
    if st.button("🔓 ফিচারগুলো আনলক করুন", type="primary"):
        if password_input == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.success("🎉 পাসওয়ার্ড সঠিক হয়েছে! বাকি পেজগুলো আনলক করা হয়েছে।")
            st.rerun()
        else:
            st.error("❌ ভুল পাসওয়ার্ড! দয়া করে সঠিক পাসওয়ার্ড দিন।")
          
