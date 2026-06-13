import streamlit as st
import sqlite3
import datetime

# ডেটাবেজ কানেকশন এবং টেবিল তৈরি
conn = sqlite3.connect('rogmukti.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
''')
conn.commit()

st.title("💸 হাসপাতালের খরচ ট্র্যাকার")

# খরচ এন্ট্রি ফর্ম
with st.form("expense_form", clear_on_submit=True):
    date = st.date_input("তারিখ", datetime.date.today())
    category = st.selectbox("খরচের খাত", ["মেডিকেল ইকুইপমেন্ট", "ওষুধ ক্রয়", "স্টাফ সেলারি", "ইউটিলিটি বিল", "অন্যান্য"])
    amount = st.number_input("টাকার পরিমাণ (BDT)", min_value=0.0, step=50.0)
    description = st.text_area("বিস্তারিত বিবরণ")
    
    submit = st.form_submit_button("খরচ যোগ করুন")

if submit:
    if amount > 0:
        c.execute("INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
                  (str(date), category, amount, description))
        conn.commit()
        st.success("✅ খরচ সফলভাবে সেভ করা হয়েছে!")
    else:
        st.error("⚠️ অনুগ্রহ করে সঠিক পরিমাণ লিখুন।")

# খরচের তালিকা দেখানো
st.subheader("📋 সাম্প্রতিক খরচের তালিকা")
c.execute("SELECT date, category, amount, description FROM expenses ORDER BY date DESC LIMIT 10")
data = c.fetchall()

if data:
    for row in data:
        st.markdown(f"**📅 {row[0]}** | 📁 *{row[1]}* : **{row[2]} BDT** — {row[3]}")
else:
    st.info("এখনো কোনো খরচের রেকর্ড নেই।")

conn.close()
