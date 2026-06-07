import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import io
from fpdf import FPDF

st.set_page_config(page_title="Rog Mukti Diagnostic Centre", layout="wide")

conn = sqlite3.connect("rogmukti_clinic_final.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, age INTEGER, phone TEXT, doctor TEXT,
    tests TEXT, total_amount REAL, discount REAL,
    advance REAL, due REAL, date TEXT, commission_pct REAL
)
""")
conn.commit()

try:
    c.execute("ALTER TABLE patients ADD COLUMN commission_pct REAL DEFAULT 0.0")
    conn.commit()
except:
    pass

TEST_PRICES = {
    "Hemoglobin (CBC)": 300, "Blood Sugar (R/F)": 150,
    "Lipid Profile": 800, "Serum Creatinine": 250,
    "Ultrasonography (USG)": 1200, "X-Ray Chest": 500,
    "ECG": 400, "Urine RE": 200
}

DOCTORS_LIST = ["Select Doctor", "Dr. Arifur Rahman (Medicine)", "Dr. Tasnim Jahan (Gynee)", "Dr. MD. Rasel (Cardiology)", "Self / None"]
def generate_pdf(patient_name, age, phone, doctor, selected_tests, total, discount, advance, due, date, inv_id):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt="ROG MUKTI DIAGNOSTIC CENTRE", ln=True, align='C')
    pdf.cell(200, 10, txt="Money Receipt / Invoice", ln=True, align='C')
    pdf.cell(200, 10, txt="--------------------------------------------------", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Invoice ID: {inv_id:05d}    |    Date: {date}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Patient Name: {patient_name}    |    Age: {age}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Phone: {phone}    |    Ref. Doctor: {doctor}", ln=True, align='L')
    pdf.cell(200, 10, txt="--------------------------------------------------", ln=True, align='L')
    pdf.cell(200, 10, txt="Selected Tests & Price:", ln=True, align='L')
    for t in selected_tests:
        pdf.cell(200, 10, txt=f" - {t}: {TEST_PRICES[t]} TK", ln=True, align='L')
    pdf.cell(200, 10, txt="--------------------------------------------------", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Total Amount: {total} TK", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Discount: {discount} TK", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Advance Paid: {advance} TK", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Due Amount: {due} TK", ln=True, align='L')
    return pdf.output(dest='S')

page = st.sidebar.radio(" মেনু নির্বাচন করুন", ["📊 ড্যাশবোর্ড ও রিপোর্ট", "🩺 নতুন রোগী ও বিলিং", "📋 পেশেন্ট ডাটাবেজ"])
if page == "📊 ড্যাশবোর্ড ও রিপোর্ট":
    st.title("📊 ডায়াগনস্টিক ড্যাশবোর্ড ও রিপোর্ট")
    st.markdown("---")
    
    c.execute("SELECT * FROM patients")
    raw_data = c.fetchall()
    
    if raw_data:
        columns = ["id", "name", "age", "phone", "doctor", "tests", "total_amount", "discount", "advance", "due", "date", "commission_pct"]
        df_dash = pd.DataFrame(raw_data, columns=columns)
        df_dash['commission_pct'] = df_dash['commission_pct'].fillna(0.0)
        df_dash['date'] = pd.to_datetime(df_dash['date'])
        
        st.subheader("🔍 ফিল্টার করুন")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            filter_type = st.selectbox("হিসাবের সময়কাল", ["সব সময়ের হিসাব", "আজকের হিসাব", "চলতি মাসের হিসাব"])
        with f_col2:
            selected_doc = st.selectbox("ডাক্তার ফিল্টার", ["সব ডাক্তার"] + DOCTORS_LIST[1:])
            
        today = datetime.now().date()
        if filter_type == "আজকের হিসাব":
            df_dash = df_dash[df_dash['date'].dt.date == today]
        elif filter_type == "চলতি মাসের হিসাব":
            df_dash = df_dash[(df_dash['date'].dt.year == datetime.now().year) & (df_dash['date'].dt.month == datetime.now().month)]
            
        if selected_doc != "সব ডাক্তার":
            df_dash = df_dash[df_dash['doctor'] == selected_doc]
                    df_dash['commission_tk'] = df_dash.apply(lambda row: (row['total_amount'] * row['commission_pct'] / 100) if row['doctor'] not in ["Self / None", "Select Doctor"] else 0, axis=1)
        
        total_earnings = df_dash['total_amount'].sum()
        total_advance = df_dash['advance'].sum()
        total_due = df_dash['due'].sum()
        total_commission = df_dash['commission_tk'].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💰 মোট বিল (Total Bill)", f"{total_earnings} TK")
        m2.metric("💵 মোট নগদ আদায়", f"{total_advance} TK")
        m3.metric("🔴 মোট বকেয়া", f"{total_due} TK", delta_color="inverse")
        m4.metric("🩺 মোট ডাক্তার কমিশন", f"{total_commission} TK")
        
        st.markdown("---")
        st.subheader("📋 ফিল্টারকৃত রোগীর তালিকা")
        df_show = df_dash[["id", "name", "phone", "doctor", "tests", "total_amount", "advance", "due", "commission_pct", "commission_tk", "date"]].copy()
        df_show.columns = ["INV ID", "নাম", "মোবাইল", "ডাক্তার", "টেস্ট সমূহ", "মোট বিল", "আদায়", "বকেয়া", "কমিশন (%)", "কমিশন (টাকা)", "তারিখ/সময়"]
        st.dataframe(df_show, use_container_width=True)
    else:
        st.info("ড্যাশবোর্ড দেখানোর জন্য ডাটাবেজে পর্যাপ্ত তথ্য নেই।")
        elif page == "🩺 নতুন রোগী ও বিলিং":
    st.title("🩺 নতুন রোগী নিবন্ধন ও বিলিং কাউন্টার")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        p_name = st.text_input("রোগীর নাম (English)")
        p_age = st.number_input("রোগীর বয়স", min_value=1, max_value=120, value=25)
        p_phone = st.text_input("মোবাইল নম্বর")
        p_doc = st.selectbox("রেফার্ড ডাক্তার", DOCTORS_LIST)
        custom_comm_pct = st.number_input("ডাক্তার কমিশন পার্সেন্টেজ (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
        
    with col2:
        selected_tests = st.multiselect("টেস্টসমূহ সিলেক্ট করুন", list(TEST_PRICES.keys()))
        subtotal = sum([TEST_PRICES[t] for t in selected_tests])
        discount = st.number_input("ছাড় / ডিসকাউন্ট (টাকা)", min_value=0.0, value=0.0)
        advance = st.number_input("অগ্রিম জমা (টাকা)", min_value=0.0, value=0.0)
        total = subtotal - discount
        due = total - advance
        
        est_commission = (total * custom_comm_pct) / 100 if p_doc not in ["Self / None", "Select Doctor"] else 0.0
        st.metric("মোট বিল (Total Bill)", f"{total} TK")
        st.metric("বকেয়া (Due Amount)", f"{due} TK")
        st.caption(f"ℹ️ এই বিলে ডাক্তারের আনুমানিক কমিশন হবে: {est_commission} TK ({custom_comm_pct}%)")
            if st.button("💾 বিল সেভ এবং রিসিট তৈরি করুন", type="primary"):
        if p_name and p_phone and selected_tests:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            tests_str = ", ".join(selected_tests)
            
            c.execute("""
                INSERT INTO patients (name, age, phone, doctor, tests, total_amount, discount, advance, due, date, commission_pct) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (p_name, p_age, p_phone, p_doc, tests_str, total, discount, advance, due, current_date, custom_comm_pct))
            conn.commit()
            st.success("✅ তথ্য সফলভাবে সংরক্ষিত হয়েছে!")
            inv_id = c.lastrowid
            
            receipt_html = f"""
            <div id="printArea" style="padding:20px; border:2px solid #333; background:#fff; color:#000; font-family:Arial;">
                <h2 style="text-align:center;margin:0;">ROG MUKTI DIAGNOSTIC CENTRE</h2>
                <p style="text-align:center;margin:5px;">Invoice ID: {inv_id:05d} | Date: {current_date}</p>
                <hr>
                <p><b>Patient Name:</b> {p_name} &nbsp;&nbsp;&nbsp;&nbsp; <b>Age:</b> {p_age}</p>
                <p><b>Phone:</b> {p_phone} &nbsp;&nbsp;&nbsp;&nbsp; <b>Doctor:</b> {p_doc}</p>
                <table style="width:100%; border-collapse:collapse; margin:15px 0;">
                    <tr style="background:#f2f2f2;"><th style="border:1px solid #ddd;padding:8px;text-align:left;">Test Name</th><th style="border:1px solid #ddd;padding:8px;text-align:right;">Price</th></tr>
                    {"".join([f"<tr><td style='border:1px solid #ddd;padding:8px;'>{t}</td><td style='border:1px solid #ddd;padding:8px;text-align:right;'>{TEST_PRICES[t]} TK</td></tr>" for t in selected_tests])}
                </table>
                <p style="text-align:right;"><b>Total Bill:</b> {total} TK</p>
                <p style="text-align:right;"><b>Advance Paid:</b> {advance} TK</p>
                <p style="text-align:right; color:red;"><b>Due Amount:</b> {due} TK</p>
            </div>
            """
            st.markdown(receipt_html, unsafe_allow_html=True)
            
            pdf_bytes = generate_pdf(p_name, p_age, p_phone, p_doc, selected_tests, total, discount, advance, due, current_date, inv_id)
            if pdf_bytes:
                st.download_button(label="📄 ডাউনলোড করুন (PDF)", data=pdf_bytes, file_name=f"Receipt_{inv_id:05d}.pdf", mime="application/pdf")
        else:
            st.error("⚠️ দয়া করে রোগীর তথ্য ও টেস্ট সঠিকভাবে সিলেক্ট করুন।")
            elif page == "📋 পেশেন্ট ডাটাবেজ":
    st.title("📋 রোগমুক্তি ক্লিনিক ডাটাবেজ")
    st.markdown("---")
    c.execute("SELECT id, name, age, phone, doctor, tests, total_amount, discount, advance, due, date, commission_pct FROM patients ORDER BY id DESC")
    data = c.fetchall()
    if data:
        columns = ["INV ID", "পেশেন্টের নাম", "বয়স", "মোবাইল নম্বর", "রেফার্ড ডাক্তার", "টেস্ট লিস্ট", "মোট বিল", "ছাড় (টাকা)", "অগ্রিম জমা", "বকেয়া", "তারিখ/সময়", "কমিশন (%)"]
        df = pd.DataFrame(data, columns=columns)
        df["INV ID"] = df["INV ID"].apply(lambda x: f"{x:05d}")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("এখনো ডাটাবেজে কোনো পেশেন্টের তথ্য রেকর্ড করা হয়নি।")
        
