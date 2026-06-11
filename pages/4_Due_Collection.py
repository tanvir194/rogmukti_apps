import sys
import os
sys.path.append(os.path.dirname(__file__))
from sidebar_monitor import show_live_sidebar
show_live_sidebar()

import streamlit as st
import sqlite3

# সিকিউরিটি চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

st.title("💰 বাকি টাকা আদায় (Due Collection)")

search_id = st.number_input("বিল নম্বর (Bill No / Invoice ID) দিয়ে খুঁজুন:", min_value=0, step=1, value=0)

if search_id > 0:
    conn = sqlite3.connect("rogmukti_clinic_fix.db")
    c = conn.cursor()
    c.execute("SELECT * FROM billing_records WHERE id = ?", (search_id,))
    row = c.fetchone()
    conn.close() 
    
    if row:
        st.success(f"🔍 রোগী পাওয়া গেছে: {row[1]} (মোবাইল: {row[3]})")
        
        current_paid = float(row[8]) if row[8] is not None else 0.0
        current_due = float(row[9]) if row[9] is not None else 0.0
        
        col1, col2 = st.columns(2)
        col1.metric("🚨 বর্তমানে বাকি আছে (Due)", f"{current_due:.2f} ৳")
        col2.metric("✅ পূর্বে জমা দিয়েছেন (Paid)", f"{current_paid:.2f} ৳")
        
        if current_due > 0:
            due_receive = st.number_input("এখন কত টাকা জমা নিতে চান?", min_value=0.0, max_value=current_due, value=current_due, step=50.0)
            
            if st.button("💰 ক্যাশ কালেকশন সেভ করুন"):
                new_paid = current_paid + due_receive
                new_due = current_due - due_receive
                
                conn = sqlite3.connect("rogmukti_clinic_fix.db")
                c = conn.cursor()
                c.execute("""
                    UPDATE billing_records 
                    SET net_paid = ?, due_amount = ? 
                    WHERE id = ?
                """, (new_paid, new_due, search_id))
                conn.commit()
                conn.close()
                
                st.success(f"✅ সফলভাবে {due_receive} ৳ জমা নেওয়া হয়েছে! নতুন বাকি: {new_due} ৳")
                st.session_state.last_invoice_id = search_id
                st.info("🖨️ নতুন আপডেটেড রিসিট তৈরি হচ্ছে, প্রিন্ট পেজে যান...")
                st.switch_page("pages/3_Print_Receipt.py")
        else:
            st.info("🎉 এই বিলের সব টাকা অলরেডি পরিশোধ করা হয়েছে! কোনো বাকি নেই।")
    else:
        st.warning("⚠️ এই বিল নম্বরের কোনো রোগীর তথ্য পাওয়া যায়নি।")
