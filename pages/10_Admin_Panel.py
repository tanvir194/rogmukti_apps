import streamlit as st
import base64

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Admin Master Control", layout="wide", initial_sidebar_state="expanded")

# ২. গ্লোবাল ডাটাবেজ ট্র্যাকিং ও সেটিংস মেমোরি
if 'test_database' not in st.session_state:
    st.session_state.test_database = {
        "CBC": 400.0,
        "Lipid Profile": 1000.0,
        "Blood Sugar": 150.0,
        "Urine RE": 250.0
    }

if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#F4F6F9"

if 'bg_data' not in st.session_state:
    st.session_state.bg_data = ""  # আপলোড করা ছবির ডাটা রাখার জন্য

# ৩. ডাইনামিক ব্যাকগ্রাউন্ড সেট করার CSS
if st.session_state.bg_data:
    # যদি কোনো ছবি আপলোড করা থাকে তবে সেটি ব্যাকগ্রাউন্ড হবে
    st.markdown(
        f"""
        <style>
        [data-testid="stMainBlockContainer"] {{
            background-image: url("data:image/png;base64,{st.session_state.bg_data}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    # কোনো ছবি না থাকলে আপনার সিলেক্ট করা কালারটি ব্যাকগ্রাউন্ড হবে
    st.markdown(
        f"""
        <style>
        [data-testid="stMainBlockContainer"] {{
            background-color: {st.session_state.bg_color} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ৪. সাইডবার মেনু কালারিং CSS
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

# ৫. মাস্টার প্যানেলের ইন্টারফেস
st.title("🛠️ Admin Master Control Panel")
st.write("এই পেজ থেকে আপনি কোনো কোড এডিট না করেই সম্পূর্ণ অ্যাপের সেটিংস নিয়ন্ত্রণ করতে পারবেন।")
st.markdown("---")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.header("🎨 ব্যাকগ্রাউন্ড ও ভিজ্যুয়াল কন্ট্রোল")
    st.info("আপনার মোবাইল বা কম্পিউটার থেকে ছবি আপলোড করুন অথবা কালার বদলান।")
    
    # ব্যাকগ্রাউন্ড কালার সিলেক্টর
    color_choice = st.color_picker("মূল পেজের ব্যাকগ্রাউন্ড কালার পরিবর্তন করুন:", st.session_state.bg_color)
    
    # 📸 সরাসরি মোবাইল বা কম্পিউটার থেকে ছবি আপলোড করার অপশন
    uploaded_file = st.file_uploader("ব্যাকগ্রাউন্ড হিসেবে ব্যবহার করার জন্য একটি ছবি আপলোড করুন (jpg, png, jpeg):", type=["jpg", "png", "jpeg"])
    
    if st.button("ভিজ্যুয়াল সেটিংস সেভ করুন"):
        st.session_state.bg_color = color_choice
        
        if uploaded_file is not None:
            # ছবিটিকে Streamlit-এর পড়ার উপযোগী Base64 ফরম্যাটে কনভার্ট করা হচ্ছে
            bytes_data = uploaded_file.read()
            base64_str = base64.b64encode(bytes_data).decode()
            st.session_state.bg_data = base64_str
            st.success("ছবি সফলভাবে আপলোড এবং ব্যাকগ্রাউন্ডে সেট হয়েছে!")
        else:
            st.session_state.bg_data = "" # ছবি না থাকলে খালি করে দেওয়া হবে
            st.success("ব্যাকগ্রাউন্ড কালার সফলভাবে আপডেট হয়েছে!")
        st.rerun()

with col2:
    st.header("🧪 টেস্ট ও প্রাইস ম্যানেজমেন্ট ফর্ম")
    st.info("নতুন টেস্ট যোগ করুন অথবা বর্তমান টেস্টের দাম পরিবর্তন করুন।")
    
    # টেস্ট এডিটিং ফর্ম (এরর ফিক্স করা হয়েছে এখানে)
    with st.form("admin_test_form", clear_on_submit=True):
        test_name = st.text_input("টেস্টের নাম লিখুন (যেমন: ECG, USG, X-Ray):")
        test_price = st.number_input("টেস্টের মূল্য নির্ধারণ করুন (BDT):", min_value=0.0, step=10.0)
        
        # সঠিক Streamlit ফর্ম বাটন ফাংশন
        submit_btn = st.form_submit_button("অ্যাপে ডাটা আপডেট করুন")
        
        if submit_btn:
            if test_name:
                st.session_state.test_database[test_name] = test_price
                st.success(f"সফল! '{test_name}' টেস্টটি {test_price} BDT মূল্যে সচল হয়েছে।")
                st.rerun()
            else:
                st.error("দয়া করে টেস্টের একটি নাম দিন।")

st.markdown("---")

# লাইভ ডাটা দেখার টেবিল
st.subheader("📋 বর্তমানে অ্যাপে সচল থাকা টেস্ট ও রেট চার্ট:")
st.dataframe(
    [{"টেস্টের নাম": name, "মূল্য (BDT)": price} for name, price in st.session_state.test_database.items()],
    use_container_width=True
)
