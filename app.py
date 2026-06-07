// যে ডাটা বা ইউজার ইনফরমেশন সার্ভারে পাঠাতে চান
const userData = {
    username: "user_name_here",
    password: "password_here"
};

// সার্ভারের API URL (আপনার সঠিক URL টি এখানে বসাবেন)
const url = 'https://example.com'; 

// Fetch API এর মাধ্যমে রিকোয়েস্ট পাঠানো
fetch(url, {
    method: 'POST', // ডাটা পাঠানোর জন্য POST মেথড
    headers: {
        'Content-Type': 'application/json' // ডাটা ফরম্যাট নির্দিষ্ট করা
    },
    body: JSON.stringify(userData) // অবজেক্টকে JSON স্ট্রিং-এ রূপান্তর
})
.then(response => {
    // রেসপন্স সফল হয়েছে কিনা চেক করা
    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }
    return response.json(); // রেসপন্স ডাটাকে JSON হিসেবে রিটার্ন করা
})
.then(data => {
    console.log('Success:', data); // সফল হলে ডাটা কনসোলে দেখাবে
    // এখানে আপনার পরবর্তী কাজগুলো (যেমন: ড্যাশবোর্ডে রিডাইরেক্ট) করতে পারেন
})
.catch(error => {
    console.error('Error:', error); // কোনো ভুল বা সমস্যা হলে তা দেখাবে
});
