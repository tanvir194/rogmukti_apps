<!-- প্রিন্ট বাটন এবং স্টাইল -->
<div style="text-align: right; margin-bottom: 20px;">
    <button onclick="window.print()" style="
        background-color: #4CAF50; 
        color: white; 
        padding: 10px 20px; 
        font-size: 16px; 
        border: none; 
        border-radius: 5px; 
        cursor: pointer;
        font-weight: bold;">
        🖨️ প্রিন্ট করুন
    </button>
</div>

<!-- শুধুমাত্র রিসিট প্রিন্ট করার জন্য CSS (যাতে সাইডবার বা অন্যান্য বাটন প্রিন্টে না আসে) -->
<style>
@media print {
    /* প্রিন্ট করার সময় প্রিন্ট বাটনটি লুকিয়ে রাখার জন্য */
    button {
        display: none !important;
    }
    /* আপনার পুরো রিসিটের প্রধান ডিভ (div) বা কন্টেইনার ছাড়া বাকি সব হাইড করতে এটি ব্যবহার করতে পারেন */
}
</style>
