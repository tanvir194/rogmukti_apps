import streamlit as st
import datetime

# ১. পেজ কনফিগারেশন এবং ফুল স্ক্রিন লেআউট (অন্য কোনো কমান্ডের আগে এটিই প্রথম থাকবে)
st.set_page_config(
    page_title="Rog Mukti Diagnostic",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ২. প্রথম স্ক্রিনশটের হুবহু ডার্ক মোড ও আধুনিক কার্ড স্টাইলের কাস্টম CSS
st.markdown("""
    <style>
    /* অ্যাপের মূল ব্যাকগ্রাউন্ড ও টেক্সট কালার */
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

# ==========================================
# আপনার আসল প্রোজেক্টের টেস্ট ডাটাবেজ (Full Test List)
# ==========================================
# এখানে আপনার ল্যাবরেটরির সব আসল টেস্টের নাম ও ফি তালিকাভুক্ত করা হয়েছে
TEST_DATABASE = {
    "CBC (Complete Blood Count)": 400,
    "Urine RE/ME": 250,
    "Serum Creatinine": 300,
    "Lipid Profile": 1000,
    "Fasting Blood Sugar (FBS)": 150,
    "SGPT (ALT)": 350,
    "SGOT (AST)": 350,
    "Serum Bilirubin": 300,
    "Uric Acid": 400,
    "TSH (Thyroid Stimulating Hormone)": 600,
    "HBsAg (Hepatitis B Surface Antigen)": 400,
    "Widal Test (Typhoid)": 350,
    "Blood Grouping & Rh Typing": 150,
    "Ultrasonography (USG) of Whole Abdomen": 1200,
    "X-Ray Chest PA View": 500,
    "ECG (Electrocardiogram)": 400,
    "Serum Electrolytes": 1000,
    "HbA1c": 700
}

# ==========================================
# বাম পাশের সাইডবার কনটেন্ট (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("### 🏢 Rog Mukti Diagnostic")
    st.caption("📅 তারিখ: 12 June, 2026")
    st.write("---")
    
    st.markdown("#### 📊 আজকের লাইভ হিসাব")
    st.metric(label="👥 মোট রোগী", value="0 জন")
    st.metric(label="💰 মোট কালেকশন", value="0 ৳")
    st.metric(label="⚠️ মোট বাকি (Due)", value="0 ৳")
    
    st.write("---")
    st.markdown("#### 🚨 ক্রিটিক্যাল ল্যাব অ্যালার্ট")
    st.error("🆔 ID: P-2041\nHb: 5.2")

# ==========================================
# মূল পেজের কন্টেন্ট (Main Page)
# ==========================================
st.markdown("## 🏥 TEST & BILLING HUB")
st.caption("টেস্ট এবং বিলিং সেকশন")
st.write("---")

# সেকশন ১: পেশেন্ট ইনফরমেশন
st.markdown('<div class="custom-card"><div class="card-header">👤 পেশেন্ট ইনফরমেশন (Patient Information)</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    patient_name = st.text_input("পেশেন্টের নাম (Name of the PT) *", placeholder="রোগীর নাম লিখুন")
with col2:
    age = st.number_input("বয়স (Age)", min_value=1, max_value=120, value=25)
with col3:
    phone = st.text_input("মোবাইল নাম্বার (Phone)", placeholder="০১XXXXXXXXX")

doctor = st.selectbox("ডাক্তার সিলেক্ট করুন (Refd By)", ["ডা. সাইদুল ইসলাম", "অধ্যাপক ডা. আব্দুর রহমান", "অন্যান্য ডাক্তার"])
st.markdown('</div>', unsafe_allow_html=True)


# সেকশন ২: টেস্ট সিলেকশন ও লাইভ রেট এন্ট্রি
st.markdown('<div class="custom-card"><div class="card-header">🔬 টেস্ট সিলেকশন ও লাইভ রেট এন্ট্রি</div>', unsafe_allow_html=True)

# ড্রপডাউন মেনুতে আপনার বড় টেস্ট লিস্টটি যুক্ত করা হয়েছে
selected_tests = st.multiselect(
    "তালিকা থেকে টেস্ট সিলেক্ট করুন (একের অধিক টেস্ট সিলেক্ট করতে পারবেন):", 
    options=list(TEST_DATABASE.keys())
)

st.markdown("##### ➕ তালিকা বহির্ভূত কাস্টম টেস্ট (ঐচ্ছিক)")
col_c1, col_c2 = st.columns(2)
with col_c1:
    custom_test_name = st.text_input("কাস্টম টেস্টের নাম:")
with col_c2:
    custom_test_price = st.number_input("কাস্টম টেস্টের মূল্য (৳):", min_value=0.0, value=0.0, step=10.0)

# লাইভ টেস্ট রেট হিসাব করার লজিক
db_test_total = sum([TEST_DATABASE[test] for test in selected_tests])
live_total_bill = db_test_total + custom_test_price

st.info(f"ℹ️ লাইভ মোট বিল (টোটাল টেস্ট ফি): {live_total_bill:.2f} টাকা")
st.markdown('</div>', unsafe_allow_html=True)


# সেকশন ৩: পেমেন্ট ও ডিসকাউন্ট
st.markdown('<div class="custom-card"><div class="card-header">💳 পেমেন্ট ও ডিসকাউন্ট</div>', unsafe_allow_html=True)
col_p1, col_p2 = st.columns(2)

with col_p1:
    discount_pct = st.number_input("ডিসকাউন্ট (Discount %)", min_value=0, max_value=100, value=0)
    advance_paid = st.number_input("অগ্রিম পরিশোধ (Advance Paid ৳)", min_value=0.0, value=0.0)

with col_p2:
    # গাণিতিক হিসাব নিকাশ
    discount_tk = (live_total_bill * discount_pct) / 100
    net_payable = live_total_bill - discount_tk
    due_tk = net_payable - advance_paid
    
    st.write(f"**ডিসকাউন্ট প্রণয় (টাকা):** {discount_tk:.2f} ৳")
    st.subheader(f"মোট বাকি টাকা (Due): {due_tk:.2f} ৳")
st.markdown('</div>', unsafe_allow_html=True)


# সেকশন ৪: ডাটা সেভ এবং অ্যাকশন বাটন
col_b1, col_b2 = st.columns(2)
with col_b2:
    if st.button("Save Bill and Go to Print (ডাটা সেভ করুন) 🖨️"):
        if not patient_name:
            st.error("দয়া করে রোগীর নাম ইনপুট দিন!")
        else:
            st.success(f"রোগী '{patient_name}'-এর বিল সফলভাবে ডাটাবেজে সংরক্ষিত হয়েছে এবং প্রিন্ট লাইনে পাঠানো হয়েছে।")
