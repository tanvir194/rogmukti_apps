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
                    <td style="font-weight: bold;">{t_name}</td>
                    <td style="text-align: center; color: #1a365d; font-weight: bold;">{t_val['result']}</td>
                    <td style="text-align: center;">{t_val['unit']}</td>
                    <td style="text-align: center; color: #555;">{t_val['ref']}</td>
                </tr>
                """
                
            report_html = f"""
            <style>
            .report-box {{
                max-width: 700px;
                margin: 10px auto;
                padding: 30px;
                border: 1px solid #ccc;
                background-color: white;
                color: black;
                font-family: 'Arial', sans-serif;
            }}
            .rep-header {{
                text-align: center;
                border-bottom: 3px double #1a365d;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .rep-header h1 {{ margin: 0; color: #1a365d; font-size: 26px; }}
            .patient-info-table {{ width: 100%; margin-bottom: 25px; border-bottom: 1px solid #1a365d; padding-bottom: 10px; }}
            .patient-info-table td {{ padding: 4px 0; font-size: 14px; }}
            .main-report-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            .main-report-table th, .main-report-table td {{ border-bottom: 1px solid #ddd; padding: 10px; text-align: left; font-size: 14px; }}
            .main-report-table th {{ background-color: #f8f9fa; color: #1a365d; }}
            .sign-section {{ margin-top: 80px; display: flex; justify-content: space-between; }}
            .signature {{ border-top: 1px solid black; width: 150px; text-align: center; font-size: 12px; padding-top: 5px; }}
            
            @media print {{
                header, footer, [data-testid="stSidebar"], [data-testid="stHeader"], .stButton, h1, h3, div.stWrite, .stnumber_input, .stTextInput {{
                    display: none !important;
                }}
                .main .block-container {{ padding: 0 !important; margin: 0 !important; }}
                .report-box {{ border: none !important; width: 100% !important; max-width: 100% !important; margin: 0 !important; padding: 0 !important; }}
                @page {{ size: A4 portrait; margin: 15mm 15mm 15mm 15mm; }}
            }}
            </style>
            
            <div class="report-box">
                <div class="rep-header">
                    <h1>রোগমুক্তি প্যাথলজি ও ডিজিটাল ল্যাব</h1>
                    <p style="margin: 5px 0 0 0; font-size: 12px; color: #555;">চিকনিকান্দি, বাউফল, পটুয়াখালী</p>
                </div>
                
                <table class="patient-info-table">
                    <tr>
                        <td><b>রোগীর নাম (Patient Name):</b> {p_name}</td>
                        <td style="text-align: right;"><b>বিল নং (Invoice ID):</b> #{search_id}</td>
                    </tr>
                    <tr>
                        <td><b>বয়স (Age):</b> {p_age} Y</td>
                        <td style="text-align: right;"><b>তারিখ (Date):</b> {p_date}</td>
                    </tr>
                    <tr>
                        <td colspan="2"><b>রেফার করা ডাক্তার (RefBy):</b> {p_doctor}</td>
                    </tr>
                </table>
                
                <h3 style="text-align: center; color: #1a365d; text-transform: uppercase; letter-spacing: 1px; font-size: 16px; margin-bottom: 15px;">BIOCHEMISTRY & PATHOLOGY REPORT</h3>
                
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
                    <div class="signature">ল্যাব টেকনোলজিস্ট</div>
                    <div class="signature">কনসালটেন্ট প্যাথলজিস্ট</div>
                </div>
            </div>
            """
            
            # প্রিন্ট বোতাম
            if st.button("🖨️ রিপোর্ট প্রিন্ট করুন (Print Report)", type="primary", use_container_width=True):
                st.components.v1.html("<script>parent.window.print();</script>", height=0)
                
            # রিপোর্ট স্ক্রিনে রেন্ডার করা
            st.html(report_html)
            
    else:
        st.error("⚠️ এই বিল নম্বরের কোনো রোগীর তথ্য পাওয়া যায়নি।")
