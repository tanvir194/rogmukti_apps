import streamlit as st
import sqlite3
import json
from datetime import datetime

# সিকিউরিটি চেক
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 অ্যাক্সেস রিফিউজড! দয়া করে আগে মেইন পেজ থেকে লগইন করুন।")
    st.stop()

st.title("🔬 প্যাথলজি রিপোর্ট জেনারেটর")
st.write("---")

# ডাটাবেজ কানেকশন ও রিপোর্ট টেবিল তৈরি
conn = sqlite3.connect("rogmukti_clinic_fix.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS pathology_reports (
    invoice_id INTEGER PRIMARY KEY,
    report_data TEXT,
    reported_date TEXT
)
""")
conn.commit()
conn.close()

search_id = st.number_input("বিল নম্বর (Invoice ID) দিয়ে রোগীর টেস্ট খুঁজুন:", min_value=0, step=1, value=0)

if search_id > 0:
    conn = sqlite3.connect("rogmukti_clinic_fix.db")
    c = conn.cursor()
    
    # রোগীর বিলের তথ্য আনা
    c.execute("SELECT patient_name, age, phone, doctor, selected_tests, billing_date FROM billing_records WHERE id = ?", (search_id,))
    patient_row = c.fetchone()
    
    # আগে থেকে এই বিলের কোনো রিপোর্ট সেভ করা আছে কি না দেখা
    c.execute("SELECT report_data FROM pathology_reports WHERE invoice_id = ?", (search_id,))
    saved_report_row = c.fetchone()
    conn.close()
    
    if patient_row:
        p_name, p_age, p_phone, p_doctor, p_tests_str, p_date = patient_row
        
        st.success(f"🔍 রোগী পাওয়া গেছে: {p_name} | ডাক্তার: {p_doctor}")
        
        # ডাটাবেজ থেকে টেস্টের নামগুলো আলাদা করা
        raw_tests = [item.strip() for item in p_tests_str.split('|') if item.strip()]
        tests_to_process = []
        for item in raw_tests:
            if ":" in item:
                tests_to_process.append(item.split(":", 1)[0])
            else:
                tests_to_process.append(item)
                
        # পূর্বে সেভ করা ডাটা থাকলে তা লোড করা
        saved_data = {}
        if saved_report_row:
            try:
                saved_data = json.loads(saved_report_row[0])
            except:
                pass

        # ✍️ রিপোর্ট ফর্ম তৈরি
        st.subheader("📝 টেস্টের ফলাফল ও রেফারেন্স ভ্যালু লিখুন")
        
        new_report_data = {}
        
        for test in tests_to_process:
            st.markdown(f"##### 🧪 টেস্ট: **{test}**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                prev_res = saved_data.get(test, {}).get("result", "")
                result = st.text_input(f"ফলাফল (Result) - {test}:", value=prev_res, key=f"res_{test}")
            with col2:
                prev_unit = saved_data.get(test, {}).get("unit", "")
                unit = st.text_input(f"ইউনিট (Unit) - {test}:", value=prev_unit, placeholder="যেমন: g/dL, mg/dL", key=f"unit_{test}")
            with col3:
                prev_ref = saved_data.get(test, {}).get("ref", "")
                ref_range = st.text_input(f"নরমাল রেঞ্জ (Reference) - {test}:", value=prev_ref, placeholder="যেমন: 12-16, <6.0", key=f"ref_{test}")
                
            new_report_data[test] = {"result": result, "unit": unit, "ref": ref_range}
            st.markdown("---")
            
        # রিপোর্ট সেভ করার বাটন
        if st.button("💾 রিপোর্টের ডাটা সেভ করুন", type="primary", use_container_width=True):
            conn = sqlite3.connect("rogmukti_clinic_fix.db")
            c = conn.cursor()
            json_str = json.dumps(new_report_data)
            current_time_str = datetime.now().strftime("%Y-%m-%d")
            
            c.execute("""
                INSERT INTO pathology_reports (invoice_id, report_data, reported_date)
                VALUES (?, ?, ?)
                ON CONFLICT(invoice_id) DO UPDATE SET report_data = ?, reported_date = ?
            """, (search_id, json_str, current_time_str, json_str, current_time_str))
            conn.commit()
            conn.close()
            st.success("✅ প্যাথলজি রিপোর্ট সফলভাবে ডাটাবেজে সেভ হয়েছে!")
            st.rerun()

        # ------------------- 🖨️ প্রিন্ট লেআউট ও ডিজাইন -------------------
        if saved_report_row:
            st.subheader("🖨️ রিপোর্ট প্রিন্ট প্রিভিউ")
            
            report_table_rows = ""
            for t_name, t_val in saved_data.items():
                report_table_rows += f"""
                <tr>
                    <td style="font-weight: bold; padding: 10px; border-bottom: 1px solid #ddd;">{t_name}</td>
                    <td style="text-align: center; color: #1a365d; font-weight: bold; padding: 10px; border-bottom: 1px solid #ddd;">{t_val['result']}</td>
                    <td style="text-align: center; padding: 10px; border-bottom: 1px solid #ddd;">{t_val['unit']}</td>
                    <td style="text-align: center; color: #555; padding: 10px; border-bottom: 1px solid #ddd;">{t_val['ref']}</td>
                </tr>
                """
                
            report_html = f"""
            <style>
            /* সাধারণ স্ক্রিন ভিউ স্টাইল */
            .report-box {{
                max-width: 700px;
                margin: 10px auto;
                padding: 35px;
                border: 2px solid #1a365d;
                border-radius: 12px;
                background-color: white;
                color: black;
                font-family: 'Arial', sans-serif;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }}
            .rep-header {{
                text-align: center;
                border-bottom: 3px double #1a365d;
                padding-bottom: 12px;
                margin-bottom: 25px;
            }}
            .rep-header h1 {{ margin: 0; color: #1a365d; font-size: 26px; }}
            .patient-info-table {{ width: 100%; margin-bottom: 25px; border-bottom: 2px solid #1a365d; padding-bottom: 12px; border-collapse: collapse; }}
            .patient-info-table td {{ padding: 6px 0; font-size: 15px; color: black; }}
            .main-report-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            .main-report-table th {{ background-color: #f2f5f9; color: #1a365d; padding: 12px 10px; text-align: left; font-size: 14px; border-bottom: 2px solid #1a365d; }}
            .sign-section {{ margin-top: 100px; display: flex; justify-content: space-between; }}
            .signature {{ border-top: 1px solid black; width: 160px; text-align: center; font-size: 13px; padding-top: 6px; color: black; }}
            
            /* 🖨️ প্রিন্ট করার সময় এই জাদুকরী স্টাইলটি কার্যকর হবে */
            @media print {{
                /* ১. স্ট্রিমলিটের অ্যাপের ভেতরের সমস্ত টেক্সট, ইনপুট বক্স, বাটন, আইকন এবং ওয়ার্নিং মেসেজ হাইড করা */
                header, footer, [data-testid="stSidebar"], [data-testid="stHeader"], .stButton, h1, h3, h5, div.stWrite, 
                [data-testid="stNumberInput"], [data-testid="stTextInput"], [data-testid="element-container"], .stAlert {{
                    display: none !important;
                    visibility: hidden !important;
                }}
                
                /* ২. স্ট্রিমলিটের মূল অ্যাপের কন্টেইনার মার্জিন শূন্য করা */
                .main .block-container {{ 
                    padding: 0 !important; 
                    margin: 0 !important; 
                }}
                
                /* ৩. শুধুমাত্র মেমো বক্সটি প্রিন্ট লেআউটে ফুল উইডথ করে দেখানো */
                .report-box {{ 
                    border: none !important; 
                    box-shadow: none !important;
                    width: 100% !important; 
                    max-width: 100% !important; 
                    margin: 0 !important; 
                    padding: 0 !important;
                    display: block !important;
                    visibility: visible !important;
                }}
                
                .report-box * {{
                    visibility: visible !important;
                }}
                
                @page {{ 
                    size: A4 portrait; 
                    margin: 15mm; 
                }}
            }}
            </style>
            
            <div class="report-box">
                <div class="rep-header">
                    <h1>রোগমুক্তি প্যাথলজি ও ডিজিটাল ল্যাব</h1>
                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #333; font-weight: bold;">চিকনিকান্দি, বাউফল, পটুয়াখালী</p>
                </div>
                
                <table class="patient-info-table">
                    <tr>
                        <td style="width: 60%;"><b>রোগীর নাম (Patient Name):</b> {p_name}</td>
                        <td style="text-align: right;"><b>বিল নং (Invoice ID):</b> #{search_id}</td>
                    </tr>
                    <tr>
                        <td><b>বয়স (Age):</b> {p_age} Years</td>
                        <td style="text-align: right;"><b>তারিখ (Date):</b> {p_date}</td>
                    </tr>
                    <tr>
                        <td colspan="2"><b>রেফার করা ডাক্তার (RefBy):</b> {p_doctor}</td>
                    </tr>
                </table>
                
                <h4 style="text-align: center; color: #1a365d; text-transform: uppercase; letter-spacing: 1px; font-size: 16px; margin: 20px 0 15px 0;">BIOCHEMISTRY & PATHOLOGY REPORT</h4>
                
                <table class="main-report-table">
                    <thead>
                        <tr>
                            <th style="width: 35%;">Test Name</th>
                            <th style="width: 20%; text-align: center;">Result</th>
                            <th style="width: 20%; text-align: center;">Unit</th>
                            <th style="width: 25%; text-align: center;">Reference Range</th>
                        </tr>
                    </thead>
                    <tbody>
                        {report_table_rows}
                    </tbody>
                </table>
                
                <div class="sign-section">
