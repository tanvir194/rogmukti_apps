import streamlit as st

st.set_page_config(page_title="Admin Unlock", layout="wide")

# লগইন ট্র্যাকিং সেশন
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

st.title("🔒 Admin Unlock Panel")
st.write("বাকি পেজগুলো দেখতে হলে এখানে পাসওয়ার্ড দিয়ে আনলক করুন।")

if st.session_state.logged_in:
    st.success("🔓 অ্যাপটি বর্তমানে আনলকড অবস্থায় আছে! আপনি এখন সাইডবারের যেকোনো পেজে যেতে পারবেন।")
    if st.button("Logout / Lock Again"):
        st.session_state.logged_in = False
        st.rerun()
else:
    # পাসওয়ার্ড ফর্ম
    password = st.text_input("সিকিউরিটি পাসওয়ার্ড দিন:", type="password")
    if st.button("Unlock All Pages"):
        if password == "admin":  # আপনার পছন্দমতো পাসওয়ার্ড দিতে পারেন
            st.session_state.logged_in = True
            st.success("সফলভাবে আনলক হয়েছে! এখন সাইডবার থেকে যেকোনো পেজে যান।")
            st.rerun()
        else:
            st.error("ভুল পাসওয়ার্ড! আবার চেষ্টা করুন।")
            
