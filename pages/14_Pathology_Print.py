import streamlit as st
import datetime

st.title("🔬 প্যাথলজি রিপোর্ট রাইটার ও প্রিন্টার")
st.write("এখানে টেস্টের রেজাল্ট লিখুন এবং সরাসরি ব্রাউজার থেকে প্রফেশনাল প্যাডে প্রিন্ট করুন।")

# ১. ইনপুট সেকশন
st.subheader("📝 রোগীর ও রিপোর্টের তথ্য দিন")
col1, col2 = st.columns(2)

with col1:
    patient_name = st.text_input("রোগীর নাম (Patient Name):", "মোঃ আব্দুর রহমান")
    patient_age = st.text_input("বয়স ও লিঙ্গ (Age/Sex):", "35Y / Male")
    test_name = st.text_input("টেস্টের নাম (Test Name):", "CBC & Blood Sugar")

with col2:
    reg_id = st.text_input("রেজিস্ট্রেশন আইডি (Reg ID):", "#RM-2026-102")
    report_date = st.date_input("রিপোর্টের তারিখ (Date):", datetime.date.today())
    ref_by = st.text_input("রেফার্ড ডাক্তার (Ref. By):", "ডাঃ সাইদুর রহমান (MBBS)")

# বড় টেক্সট বক্স রেজাল্ট লেখার জন্য
st.markdown("---")
st.subheader("📊 টেস্ট রেজাল্ট ও বিবরণ লিখুন")
report_details = st.text_area(
    "এখানে আপনার রিপোর্টের মূল টেবিল বা টেক্সট লিখুন (HTML ফরম্যাটও সাপোর্ট করবে):", 
    value="Hemoglobin: 14.5 g/dL (Normal: 13.5-17.5)\nRBC Count: 4.8 million/µL\nBlood Sugar (RBS): 6.2 mmol/L",
    height=200
)

# ২. এইচটিএমএল (HTML) দিয়ে প্রফেশনাল রিপোর্টের প্যাড ডিজাইন
# টেক্সটের নিউলাইন (\n) কে এইচটিএমএল ব্রেকিং ট্যাগে (<br>) রূপান্তর
formatted_details = report_details.replace("\n", "<br>")

report_html = f"""
<div class="print-area">
    <!-- হাসপাতালের হেডার প্যাড -->
    <div style="text-align: center; border-bottom: 3px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 20px;">
        <h1 style="color: #1E3A8A; margin: 0; font-size: 28px; font-weight: bold; text-transform: uppercase;">Rog Mukti Diagnostic Centre</h1>
        <p style="margin: 5px 0 0 0; color: #555; font-size: 14px;">Mollah stand, Auliaspur, Patuakhali | Mobile: 01711857837</p>
        <h3 style="background-color: #1E3A8A; color: white; display: inline-block; padding: 5px 15px; border-radius: 4px; margin-top: 10px; font-size: 16px;">PATHOLOGY REPORT</h3>
    </div>

    <!-- রোগীর তথ্যের টেবিল -->
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px; background-color: #F9FAFB; border: 1px solid #E5E7EB;">
        <tr>
            <td style="padding: 8px; border: 1px solid #E5E7EB;"><strong>Patient Name:</strong> {patient_name}</td>
            <td style="padding: 8px; border: 1px solid #E5E7EB;"><strong>Reg ID:</strong> {reg_id}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #E5E7EB;"><strong>Age / Sex:</strong> {patient_age}</td>
            <td style="padding: 8px; border: 1px solid #E5E7EB;"><strong>Date:</strong> {report_date}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #E5E7EB;"><strong>Ref. By:</strong> {ref_by}</td>
            <td style="padding: 8px; border: 1px solid #E5E7EB;"><strong>Test Name:</strong> <span style="color: #1E3A8A; font-weight: bold;">{test_name}</span></td>
        </tr>
    </table>

    <!-- টেস্টের মূল রেজাল্ট এরিয়া -->
    <div style="min-height: 250px; border: 1px solid #E5E7EB; padding: 20px; border-radius: 6px; font-family: monospace; font-size: 16px; line-height: 1.6; background-color: #fff;">
        <strong style="font-family: sans-serif; color: #1E3A8A; display: block; border-bottom: 1px solid #EEE; padding-bottom: 5px; margin-bottom: 15px;">FINDINGS / RESULTS:</strong>
        {formatted_details}
    </div>

    <!-- ফুটার সিগনেচার সেকশন -->
    <div style="margin-top: 80px; width: 100%;">
        <table style="width: 100%; font-size: 14px;">
            <tr>
                <td style="width: 50%; text-align: left; color: #777;">_______________________<br>Prepared By (Lab Technologist)</td>
                <td style="width: 50%; text-align: right; color: #777;">_______________________<br>Authorized Signatory (Pathologist)</td>
            </tr>
        </table>
    </div>
</div>

<!-- জাভাস্ক্রিপ্ট দিয়ে উইন্ডো প্রিন্ট করার প্রফেশনাল বাটন এবং সিএসএস প্রিন্ট মিডিয়া কন্ট্রোল -->
<style>
@media print {{
    /* প্রিন্ট করার সময় সাইডবার, অন্যান্য বাটন এবং স্ট্রিমলিটের ডিফল্ট জিনিস লুকিয়ে ফেলা */
    [data-testid="stSidebar"], button, header, [data-testid="stHeader"], .stButton {{
        display: none !important;
    }}
    .print-area {{
        width: 100% !important;
        max-width: 100% !important;
        box-shadow: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
}}
</style>
"""

# স্ক্রিনে রিপোর্টটির একটি প্রিভিউ দেখানো
st.markdown("---")
st.subheader("👁️ রিপোর্টের প্রিভিউ (Preview)")
st.markdown(report_html, unsafe_allow_html=True)

st.markdown("---")
# ৩. সরাসরি প্রিন্ট ট্রিগার করার বাটন
if st.button("🖨️ সরাসরি রিপোর্ট প্রিন্ট করুন (কম্পিউটার/মোবাইল)", type="primary", use_container_width=True):
    # এই জাভাস্ক্রিপ্ট কোডটি ব্রাউজারের প্রিন্ট ডায়ালগ বক্স ওপেন করে দেবে (মোবাইলে পিডিএফ সেভ অপশন আসবে)
    st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
