import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import io
from fpdf import FPDF

# পেজ কনফিগারেশন
st.set_page_config(page_title="Rog Mukti Diagnostic Centre", layout="wide")

# ডাটাবেজ কানেকশন
conn = sqlite3.connect("rogmukti_clinic_final.db", check_same_thread=False)
c = conn.cursor()

# টেবিল তৈরি
c.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    phone TEXT,
    doctor TEXT,
    tests TEXT,
    total_amount REAL,
    discount,
    advance,
    due REAL,
    date TEXT
)
""")
conn.commit()

# PDF তৈরি করার নতুন ফাংশন
def generate_pdf(receipt_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in receipt_text.split('\n'):
        clean_line = line.replace('<br>', '').replace('<b>', '').replace('</b>', '').replace('</div>', '').replace('<tr>', '')
        if clean_line.strip() and not clean_line.startswith('<'):
            pdf.cell(200, 10, txt=clean_line.strip().encode('utf-8', 'ignore').decode('utf-8'), ln=True, align='L')
    return pdf.output(dest='S')
# এখানে আপনার মূল বিলিং এবং রিসিট তৈরির কোড থাকবে
# (আপনার আগের app.py ফাইল থেকে ৩৪০ নম্বর লাইন পর্যন্ত কোড)

# উদাহরণস্বরূপ জাভাস্ক্রিপ্ট প্রিন্ট বাটন এবং html_receipt এর অংশ:
print_button_html = f"""
<script>
function printInvoice() {{
    var printContents = document.getElementById('printArea').innerHTML;
    var originalContents = document.body.innerHTML;
    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;
    window.location.reload();
}}
</script>
<button onclick="printInvoice()" style="background-color: #1e3a8a; color: white; padding: 12px 24px; font-size: 16px;">
🖨️ প্রিন্ট করুন (Print Receipt)
</button>
<br><br>
{{html_receipt}}
"""

st.components.v1.html(print_button_html, height=720, scrolling=True)

# নিচে আমাদের নতুন PDF ডাউনলোড বাটন
pdf_data = generate_pdf(html_receipt)
if pdf_data:
    st.download_button(
        label="📄 ডাউনলোড করুন (PDF)",
        data=pdf_data,
        file_name="Diagnostic_Report.pdf",
        mime="application/pdf"
    )
elif page == "পেশেন্ট ডাটাবেজ":
    st.title("📋 রোগমুক্তি ক্লিনিক ডাটাবেজ")
    st.markdown("---")
    
    c.execute("SELECT * FROM patients ORDER BY id DESC")
    data = c.fetchall()
    
    if data:
        columns = ["INV ID", "পেশেন্টের নাম", "বয়স", "মোবাইল নম্বর", "রেফার্ড ডাক্তার", "টেস্ট লিস্ট", "মোট বিল", "ছাড় (%)", "অগ্রিম", "বকেয়া", "তারিখ"]
        df = pd.DataFrame(data, columns=columns)
        df["INV ID"] = df["INV ID"].apply(lambda x: f"{x:05d}")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("এখনো ডাটাবেজে কোনো পেশেন্টের তথ্য রেকর্ড করা হয়নি।")
