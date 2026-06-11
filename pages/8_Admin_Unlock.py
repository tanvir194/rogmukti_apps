import streamlit as st
import base64

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="Admin Master Control", layout="wide", initial_sidebar_state="expanded")

# ২. গ্লোবাল মেমোরি ট্র্যাকিং (যা অন্য পেজেও কাজ করবে)
if 'test_database' not in st.session_state:
    st.session_state.test_database = {
        "CBC": 410.0,
        "Lipid Profile": 1010.0,
        "Blood Sugar": 150.0,
        "Urine RE": 250.0
    }

# ডিফোল্ট ব্যাকগ্রাউন্ড সেটিংস
if 'global_bg_color' not in st.session_state:
    st.session_state.global_bg_color = "#2085A6" # আপনার স্ক্রিনশটের বর্তমান সুন্দর নীল কালারটি ডিফল্ট রাখলাম

if 'global_bg_data' not in st.session_state:
    st.session_state.global_bg_data = ""

# ৩. এই কোডটুকু ম্যাজিকের মতো আপনার পুরো অ্যাপের প্রতিটা পেজের ব্যাকগ্রাউন্ড কন্ট্রোল করবে
def apply_global_theme():
    if st.session_state.global_bg_data:
        bg_css = f"""
        <style>
        [data-testid="stMainBlockContainer"], [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{st.session_state.global_bg_data}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        </style>
        """
    else:
        bg_css = f"""
        <style>
        [data-testid="stMainBlockContainer"], [data-testid="stAppViewContainer"] {{
            background-color: {st.session_state.global_bg_color} !important;
            background-image: none !important;
        }}
        </style>
        """
    
    # সাইডবার মেনুর লেখার স্টাইল ও কালার
    sidebar_css = """
    <style>
    [data-testid="stSidebarNavLink"] span {
        color: #0066CC !important; 
        font-weight: bold !important; 
    }
    </style>
    """
    st.markdown(bg_css + sidebar_css, unsafe_allow_html=True)

# থিম অ্যাপ্লাই করা হলো
apply_global_theme()

# ৪. মাস্টার প্যানেলের মেইন ইন্টারফেস
st.title("🛠️ Admin Master Control Panel")
st.write("এখানে ছবি আপলোড করলে বা কালার পরিবর্তন করলে তা সাইডবারের **প্রতিটি পেজে** একবারে কাজ করবে।")
st.markdown("---")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.header("🎨 সম্পূর্ণ অ্যাপের ভিজ্যুয়াল কন্ট্রোল")
    st.info("আপনার মোবাইল/কম্পিউটার থেকে ছবি আপলোড করুন অথবা কালার নির্বাচন করুন।")
    
    # কালার পিকার
    color_choice = st.color_picker("সব পেজের ব্যাকগ্রাউন্ড কালার সিলেক্ট করুন:", st.session_state.global_bg_color)
    
    # সরাসরি ডিভাইস থেকে ফাইল আপলোডার
    uploaded_file = st.file_uploader("সব পেজের ব্যাকগ্রাউন্ডের জন্য ছবি আপロード করুন:", type=["jpg", "png", "jpeg"])
    
    if st.button("ভিজ্যুয়াল সেটিংস সেভ করুন (সব পেজের জন্য)"):
        st.session_state.global_bg_color = color_choice
        
        if uploaded_file is not None:
            # ছবিকে মেমোরিতে সেভ করার জন্য বাইনারি কনভার্ট করা
            bytes_data = uploaded_file.read()
            base64_str = base64.b64encode(bytes_data).decode()
            st.session_state.global_bg_data = base64_str
            st.success("🎉 ছবি সফলভাবে আপলোড হয়েছে! এখন অন্য পেজে গিয়ে চেক করুন।")
        else:
            st.session_state.global_bg_data = ""
            st.success("🎨 ব্যাকগ্রাউন্ড কালার সফলভাবে পরিবর্তন হয়েছে!")
        st.rerun()

with col2:
    st.header("🧪 টেস্ট ও প্রাইস ম্যানেজমেন্ট ফর্ম")
    st.info("নতুন টেস্ট যোগ করুন বা বর্তমান টেস্টের রেট এডিট করুন।")
    
    with st.form("admin_test_form", clear_on_submit=True):
        test_name = st.text_input("টেস্টের নাম লিখুন:")
        test_price = st.number_input("টেস্টের মূল্য নির্ধারণ করুন (BDT):", min_value=0.0, step=10.0)
        
        submit_btn = st.form_submit_button("অ্যাপে ডাটা আপডেট করুন")
        if submit_btn:
            if test_name:
                st.session_state.test_database[test_name] = test_price
                st.success(f"সফল! '{test_name}' টেস্টের নতুন মূল্য {test_price} BDT সেট হয়েছে।")
                st.rerun()
            else:
                st.error("দয়া করে টেস্টের একটি নাম দিন।")

st.markdown("---")

# লাইভ ডাটা টেবিল
st.subheader("📋 বর্তমানে অ্যাপে সচল থাকা টেস্ট ও রেট চার্ট:")
st.dataframe(
    [{"টেস্টের নাম": name, "মূল্য (BDT)": price} for name, price in st.session_state.test_database.items()],
    use_container_width=True
)
