import streamlit as st

# ১. ইনভয়েস আইডি ইনপুট বক্স
invoice_id = st.number_input("Enter Bill No / Invoice ID to Print:", min_value=1, value=11, step=1)

# ২. এইচটিএমএল ডিজাইন (কোনো f-string বা পাইথন ক্যাটিনেশন ছাড়া সাধারণ টেক্সট)
html_receipt = """
<!-- প্রিন্ট অ্যাকশন বাটন -->
<div style="text-align: right; margin-bottom: 20px;">
    <button onclick="window.print()" style="
        background-color: #4CAF50; 
        color: white; 
        padding: 12px 24px; 
        font-size: 16px; 
        border: none; 
        border-radius: 5px; 
        cursor: pointer;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        🖨️ রিসিটটি প্রিন্ট করুন
    </button>
</div>

<!-- মানি রিসিটের প্রধান বডি -->
<div id="receipt-body" style="font-family: 'Arial', sans-serif; padding: 20px; border: 1px solid #ddd; background: #fff; color: #000;">
    
    <!-- ডায়াগনস্টিক সেন্টারের হেডার -->
    <div style="text-align: center; border-bottom: 2px double #000; padding-bottom: 10px;">
        <h1 style="font-size: 32px; font-weight: bold; margin: 0; color: #000;">ডায়াগনস্টিক সেন্টার এর নাম</h1>
        <p style="font-size: 15px; margin: 5px 0 0 0;">মহল্লা স্ট্যান্ড, আউলিয়াাবাদ</p>
        <p style="font-size: 15px; font-weight: bold; margin: 3px 0 0 0;">মানি রিসিট (A4 সাইজ)</p>
    </div>

    <!-- পেশেন্ট ইনফরমেশন টেবিল -->
    <table style="width: 100%; font-size: 16px; margin-top: 25px; margin-bottom: 25px; line-height: 1.6; border-collapse: collapse;">
        <tr>
            <td style="width: 50%;"><b>Invoice ID:</b> <span id="bill-id-placeholder"></span></td>
            <td style="text-align: right; width: 50%;"><b>Date:</b> 2026-06-13</td>
        </tr>
        <tr>
            <td><b>Patient Name:</b> Demo Patient</td>
            <td style="text-align: right;"><b>Age/Sex:</b> 25 Y/M</td>
        </tr>
        <tr>
            <td><b>Mobile No:</b> 01711867637</td>
            <td style="text-align: right;"><b>Ref. By:</b> Dr. Abdur Rahman</td>
        </tr>
    </table>

    <!-- টেস্ট ও ফি-এর মেইন টেবিল -->
    <table style="width: 100%; border-collapse: collapse; font-size: 16px; margin-top: 15px;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="width: 10%; border: 1px solid #000; padding: 10px; text-align: center;">SL</th>
                <th style="width: 65%; border: 1px solid #000; padding: 10px; text-align: left;">Test Name</th>
                <th style="width: 25%; border: 1px solid #000; padding: 10px; text-align: right;">Price (Tk)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="border: 1px solid #000; padding: 10px; text-align: center;">1</td>
                <td style="border: 1px solid #000; padding: 10px;">CBC with ESR</td>
                <td style="border: 1px solid #000; padding: 10px; text-align: right;">400.00</td>
            </tr>
            <tr>
                <td style="border: 1px solid #000; padding: 10px; text-align: center;">2</td>
                <td style="border: 1px solid #000; padding: 10px;">Serum Creatinine</td>
                <td style="border: 1px solid #000; padding: 10px; text-align: right;">300.00</td>
            </tr>
        </tbody>
    </table>

    <!-- ফাইনাল বিলের হিসাব বক্স -->
    <div style="margin-top: 25px; float: right; width: 45%; font-size: 16px;">
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 5px; text-align: left;"><b>Total Bill:</b></td>
                <td style="text-align: right; padding: 5px;">700.00 Tk</td>
            </tr>
            <tr style="border-bottom: 1px solid #dddddd;">
                <td style="padding: 5px; text-align: left;"><b>Discount:</b></td>
                <td style="text-align: right; padding: 5px;">0.00 Tk</td>
            </tr>
            <tr style="border-bottom: 1px solid #dddddd;">
                <td style="padding: 5px; text-align: left;"><b>Advance Paid:</b></td>
                <td style="text-align: right; padding: 5px;">700.00 Tk</td>
            </tr>
            <tr style="border-top: 1px solid #000000; font-size: 18px; font-weight: bold;">
                <td style="padding: 5px; text-align: left;">Due Amount:</td>
                <td style="text-align: right; padding: 5px;">0.00 Tk</td>
            </tr>
        </table>
    </div>
    <div style="clear: both;"></div>

</div>

<!-- ৩. জাভাস্ক্রিপ্ট দিয়ে ইনপুট বক্সের মান রিসিটে পাঠানো -->
<script>
    document.getElementById("bill-id-placeholder").innerText = "PLACEHOLDER_ID";
</script>

<!-- ৪. প্রিন্ট করার জন্য বিশেষ সিএসএস -->
<style>
@media print {
    [data-testid="stSidebar"], 
    header, 
    footer, 
    button {
        display: none !important;
    }
    
    .main .block-container {
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }
}
</style>
"""

# ইনপুট বক্সের আইডিটি এইচটিএমএল-এ ডাইনামিকালি সেট করা
final_html = html_receipt.replace("PLACEHOLDER_ID", str(invoice_id))

# ৩. ফাইনাল আউটপুট রেন্ডার করা
st.markdown(final_html, unsafe_allow_html=True)
