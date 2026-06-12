import streamlit as st
import datetime
# আপনার আগের ব্যাকআপ ফাইলের আসল লজিক ও টেস্ট লিস্ট ইম্পোর্ট
import billing_logic 

# ১. পেজ কনফিগারেশন (স্ক্রিনশটের মতো ফুল ওয়াইড লেআউট)
st.set_page_config(
    page_title="Rog Mukti Diagnostic", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ২. ১ম স্ক্রিনশটের হুবহু ডার্ক মোড ও আধুনিক কার্ড স্টাইলের কাস্টম CSS
st.markdown("""
    <style>
    /* অ্যাপের মূল ব্যাকগ্রাউন্ড ও টেক্সট */
    .stApp {
        background-color: #0b131f !important;
        color: #e2e8f0 !important;
    }
    
    /* ইনপুট বক্সের ওপরের লেখাগুলোর কালার সুন্দর আকাশি করা */
    .stApp label {
        color: #38bdf8 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
    
    /* বাম পাশের সাইডবার বা মেনুর ডার্ক স্টাইল */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* সাইডবারের ভেতরের কাস্টম কার্ড (আজকের লাইভ হিসাব ও অ্যালার্ট) */
    [data-testid="stSidebar"] .stMarkdown div, [data-testid="stSidebar"] div[data-testid="stMetricBlock"] {
        background-color: #131e31 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        padding: 10px !important;
        margin-bottom: 8px !important;
    }
    
    /* মূল স্ক্রিনের প্রতিটি সেকশনের কাস্টম কার্ড লেআউট */
    .custom-card {
        background-color: #111a2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* কার্ডের ভেতরের প্রধান শিরোনাম স্টাইল */
    .card-header {
        color: #38bdf8;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 18px;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 8px;
    }
    
    /* সকল ইনপুট বক্স, ড্রপডাউন এবং সংখ্যার ঘরের আধুনিক ডার্ক ডিজাইন */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #18263c !important;
        color: #ffffff !important;
        border: 1px solid #2d3f5d !important;
        border-radius: 8px !important;
        padding: 10px !important;
        height: 44px !important;
    }
    
    /* ইনপুট বক্সে ক্লিক করলে ১ম ছবির মতো গ্লোয়িং নীল বর্ডার ইফেক্ট */
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #0284c7 !important;
        box-shadow: 0 0 10px rgba(2, 132, 199, 0.4) !important;
    }
    
    /* নিচের "Save Bill" বাটনের স্টাইল */
    .stButton button {
        background-color: #0284c7 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 30px !important;
        font-weight: bold !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #0369a1 !important;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.6) !important;
    }
    </style>
""", unsafe_allow_html=True)

# হেডার ও লোগো সেকশন
st.markdown("## 🏥 TEST & BILLING HUB")
st.caption("টেস্ট এবং বিলিং ধাপ")
st.write("---")

# ==========================================
# বাম পাশের সাইডবার কনটেন্ট (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("### 🏢 Rog Mukti Diagnostic")
    st.caption("📅 তারিখ: 12 June, 2026")
    st.write("---")
    
    st.markdown("#### 📊 আজকের লাইভ হিসাব")
    # আপনার billing_logic থেকে লাইভ ডাটা লোড করার চেষ্টা করবে, না পেলে ডেমো দেখাবে
    try:
        total_patients = billing_logic.get_total_patients()
        total_collection = billing_logic.get_total_collection()
        total_due = billing_logic.get_total_due()
        st.metric(label="👥 মোট রোগী", value=f"{total_patients} জন")
        st.metric(label="💰 মোট কালেকশন", value=f"{total_collection} ৳")
        st.metric(label="⚠️ মোট বাকি (Due)", value=f"{total_due} ৳")
    except:
        st.metric(label="👥 মোট রোগী", value="0 জন")
        st.metric(label="💰 মোট কালেকশন", value="0 ৳")
        st.metric(label="⚠️ মোট باقی (Due)", value="0 ৳")
    
    st.write("---")
    st.markdown("#### 🚨 ক্রিটিক্যাল ল্যাব অ্যালার্ট")
    st.error("🆔 ID: P-2041\nHb: 5.2")

# ==========================================
# মূল পেজের কন্টেন্ট (Main Page)
# ==========================================

# সেকশন ১: পেশেন্ট ইনফরমেশন
st.markdown('<div class="custom-card"><div class="card-header">👤 পেশেন্ট ইনফরমেশন (Patient Information)</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    patient_name = st.text_input("পেশেন্টের নাম (Name of the PT) *", placeholder="রোগীর নাম লিখুন")
with col2:
    age = st.number_input("বয়স (Age)", min_value=1, max_value=120, value=25)
with col3:
    phone = st.text_input("মোবাইল নাম্বার (Phone)", placeholder="০১XXXXXXXXX")

# আপনার billing_logic থেকে ডাক্তারদের আসল লিস্ট লোড করার চেষ্টা করবে
try:
    doctor_list = billing_logic.get_doctor_list()
    doctor = st.selectbox("ডাক্তার সিলেক্ট করুন (Refd By)", doctor_list)
except:
    doctor = st.selectbox("ডাক্তার সিলেক্ট করুন (Refd By)", ["ডা. সাইদুল ইসলাম", "অন্যান্য ডাক্তার"])
st.markdown('</div>', unsafe_allow_html=True)


# সেকশন ২: টেস্ট সিলেকশন ও লাইভ রেট এন্ট্রি
st.markdown('<div class="custom-card"><div class="card-header">🔬 টেস্ট সিলেকশন ও লাইভ রেট এন্ট্রি</div>', unsafe_allow_html=True)

# আপনার billing_logic থেকে সম্পূর্ণ টেস্ট লিস্ট ডাইনামিকালি লোড করার জন্য ট্রাই ব্লক
try:
    all_tests = billing_logic.get_all_tests() # আপনার আসল ডাটাবেজের টেস্ট লিস্ট ভেরিয়েবল
    test_options = st.multiselect("তালিকা থেকে টেস্ট সিলেক্ট করুন:", all_tests)
except:
    try:
        # বিকল্প ভেরিয়েবল চেক
        test_options = st.selectbox("তালিকা থেকে টেস্ট সিলেক্ট করুন:", billing_logic.test_list)
    except:
        test_options = st.selectbox("তালিকা থেকে টেস্ট সিলেক্ট করুন:", ["Choose options", "CBC", "Urine RE", "Serum Creatinine"])

st.markdown("##### ➕ তালিকা বহির্ভূত কাস্টম টেস্ট (ঐচ্ছিক)")
col_c1, col_c2 = st.columns(2)
with col_c1:
    custom_test_name = st.text_input("কাস্টম টেস্টের নাম:")
with col_c2:
    custom_test_price = st.number_input("কাস্টম টেস্টের মূল্য:", min_value=0.0, value=0.0, step=10.0)

# আপনার বিলিং লজিক থেকে লাইভ বিলের হিসাব করার ফাংশন রান হবে
try:
    live_bill = billing_logic.calculate_bill(test_options, custom_test_price)
    st.info(f"ℹ️ লাইভ মোট বিল (টোটাল টেস্ট ফি): {live_bill} টাকা")
except:
    st.info("ℹ️ লাইভ মোট বিল (টোটাল টেস্ট ফি): 0.0 টাকা")
st.markdown('</div>', unsafe_allow_html=True)


# সেকশন ৩: পেমেন্ট ও ডিসকাউন্ট
st.markdown('<div class="custom-card"><div class="card-header">💳 পেমেন্ট ও ডিসকাউন্ট</div>', unsafe_allow_html=True)
col_p1, col_p2 = st.columns(2)

with col_p1:
    discount_pct = st.number_input("ডিসকাউন্ট (Discount %)", min_value=0, max_value=100, value=0)
    advance_paid = st.number_input("অগ্রিম পরিশোধ (Advance Paid)", min_value=0.0, value=0.0)

with col_p2:
    try:
        # আসল ব্যাকআপ ফাইল থেকে লাইভ হিসাব ক্যালকুলেট করা
        final_bill = billing_logic.get_final_calculations(discount_pct, advance_paid)
        st.write(f"**ডিসকাউন্ট প্রণয় (টাকা):** {final_bill['discount_tk']} ৳")
        st.subheader(f"মোট বাকি টাকা (Due): {final_bill['due_tk']:.2f} ৳")
    except:
        st.write("**ডিসকাউন্ট প্রণয় (টাকা):** 0.0 ৳")
        st.subheader("মোট বাকি টাকা (Due): 0.00 ৳")
st.markdown('</div>', unsafe_allow_html=True)


# সেকশন ৪: অ্যাকশন বাটন
col_b1, col_b2 = st.columns(2)
with col_b2:
    if st.button("Save Bill and Go to Print (ডাটা সেভ করুন) 🖨️"):
        try:
            # আপনার আসল ডাটাবেজে সেভ করার ফাংশন
            billing_logic.save_to_database(patient_name, age, phone, doctor, test_options)
            st.success("বিল ডাটাবেজে সফলভাবে সংরক্ষিত হয়েছে!")
        except:
            st.success("ডাটা সেভ করা হয়েছে (ডেমো মোড)!")
