import streamlit as st
import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect('rogmukti.db')
c = conn.cursor()

st.title("📊 অ্যানালিটিক্স ড্যাশবোর্ড")

# ১. মোট রোগী গণনা
try:
    c.execute("SELECT COUNT(*) FROM patients")
    total_patients = c.fetchone()[0]
except:
    total_patients = 0

# ২. মোট খরচ গণনা
try:
    c.execute("SELECT SUM(amount) FROM expenses")
    total_expense = c.fetchone()[0] or 0.0
except:
    total_expense = 0.0

# ৩. মোট আয় গণনা
try:
    c.execute("SELECT SUM(amount_paid) FROM due_collection")
    total_income = c.fetchone()[0] or 0.0
except:
    total_income = 0.0

# ড্যাশবোর্ড কার্ড বা সামারি
col1, col2, col3 = st.columns(3)
col1.metric("👥 মোট নিবন্ধিত রোগী", f"{total_patients} জন")
col2.metric("💰 মোট সংগ্রহ/আয়", f"{total_income} BDT")
col3.metric("📉 মোট খরচ", f"{total_expense} BDT")

st.write("---")

# আয় বনাম খরচের গ্রাফিক্যাল চার্ট
st.subheader("📈 আয় এবং খরচের তুলনা")
if total_income > 0 or total_expense > 0:
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # ডার্ক থিমের ব্যাকগ্রাউন্ড সেটআপ
    fig.patch.set_facecolor('#1a1a1a')
    ax.set_facecolor('#1a1a1a')
    
    categories = ['মোট আয়', 'মোট খরচ']
    values = [total_income, total_expense]
    colors = ['#2ecc71', '#e74c3c']
    
    bars = ax.bar(categories, values, color=colors, width=0.4)
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + (yval*0.01), f"{yval} BDT", ha='center', va='bottom', color='white')

    st.pyplot(fig)
else:
    st.info("গ্রাফ দেখানোর জন্য পর্যাপ্ত আয় বা খরচের ডেটা নেই।")

conn.close()
