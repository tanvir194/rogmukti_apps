import streamlit as st

# ১. এই নতুন কন্ট্রোল পেজের কনফিগারেশন
st.set_page_config(page_title="Admin Master Control", layout="wide", initial_sidebar_state="expanded")

# ২. গ্লোবাল ডাটাবেজ ট্র্যাকিং (যাতে অন্য পেজের ডাটা এখানে আপডেট করা যায়)
if 'test_database' not in st.session_state:
    st.session_state.test_database = {
        "CBC": 400.0,
        "Lipid Profile": 1000.0,
        "Blood Sugar": 150.0,
        "Urine RE": 250.0
    }

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#F4F6F9"

if 'bg_image' not in st.session_state:
    st.session_state.bg_image = ""

# ৩. কালারিং সেটিংস (এই পেজের জন্য)
st.markdown(
    """
    <style>
    [data-testid="stSidebarNavLink"] span {
        color: #0066CC !important; 
        font-weight: bold !important; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ৪. মাস্টার প্যানেলের মূল ইন্টারফেস
st.title("🛠️ Admin Master Control Panel")
st.write("এই পেজ থেকে আপনি কোনো কোড এডিট না করেই সম্পূর্ণ অ্যাপের সেটিংস নিয়ন্ত্রণ করতে পারবেন।")

st.markdown("---")

# দুইটি আলাদা বিভাগ তৈরি করা হলো
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("🎨 ব্যাকগ্রাউন্ড ও ভিজ্যুয়াল কন্ট্রোল")
    st.info("এখানে পরিবর্তন করলে অ্যাপের ব্যাকগ্রাউন্ড আপডেট হবে।")
    
    # ব্যাকগ্রাউন্ড কালার সিলেক্টর
    color_choice = st.color_picker("মূল পেজের ব্যাকগ্রাউন্ড কালার পরিবর্তন করুন:", st.session_state.bg_color)
    
    # ব্যাকগ্রাউন্ড ছবি পরিবর্তনের ইনপুট
    image_url = st.text_input("ব্যাকগ্রাউন্ড ছবির অনলাইন লিংক (URL) দিন:", st.session_state.bg_image)
    
    if st.button("ভিজ্যুয়াল সেটিংস সেভ করুন"):
        st.session_state.bg_color = color_choice
        st.session_state.bg_image = image_url
        st.success("ব্যাকগ্রাউন্ড সেটিংস সফলভাবে আপডেট হয়েছে!")
        st.rerun()

with col2:
    st.header("🧪 টেস্ট ও প্রাইস ম্যানেজমেন্ট ফর্ম")
    st.info("নতুন টেস্ট যোগ করুন অথবা বর্তমান টেস্টের দাম পরিবর্তন করুন।")
    
    # টেস্ট এডিটিং ফর্ম
    with st.form("admin_test_form", clear_on_submit=True):
        test_name = st.text_input("টেস্টের নাম লিখুন (যেমন: ECG, USG, X-Ray):")
        test_price = st.number_input("টেস্টের মূল্য নির্ধারণ করুন (BDT):", min_value=0.0, step=10.0)
        
        submit_btn = st.form_submit_with_button("অ্যাপে ডাটা আপডেট করুন")
        
        if submit_btn:
            if test_name:
                # সেশন স্টেটে ডাটা সেভ হচ্ছে
                st.session_state.test_database[test_name] = test_price
                st.success(f"ম্যাজিক! '{test_name}' টেস্টটি {test_price} BDT মূল্যে সচল হয়েছে।")
            else:
                st.error("দয়া করে টেস্টের একটি নাম দিন।")

st.markdown("---")

# ৫. বর্তমান লাইভ ডাটা দেখার টেবিল
st.subheader("📋 বর্তমানে অ্যাপে সচল থাকা টেস্ট ও রেট চার্ট:")
st.dataframe(
    [{"টেস্টের নাম": name, "মূল্য (BDT)": price} for name, price in st.session_state.test_database.items()],
    use_container_width=True
)

