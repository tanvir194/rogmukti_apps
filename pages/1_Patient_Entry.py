import streamlit as st
import datetime

# ১. পেজ কনফিগারেশন এবং ফুল স্ক্রিন লেআউট
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
    
    /* সাইডবারের ভেতরের কাস্টম কার্ড */
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
    
    /* ইনপুট বক্সে ক্লিক করলে গ্লোয়িং নীল বর্ডার ইফেক্ট */
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
