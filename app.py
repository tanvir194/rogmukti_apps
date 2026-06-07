import datetime

# ১. টেস্ট প্রাইস লিস্ট ডিকশনারি
TEST_PRICES = {
    "CBC (Complete Blood Count)": 400.0,
    "Hgb (Hemoglobin)": 150.0,
    "ESR (Erythrocyte Sedimentation Rate)": 250.0,
    "WBC Count & DC": 250.0,
    "Platelet Count": 200.0,
    "Blood Grouping & Rh Typing": 150.0,
    "BT & CT (Bleeding & Clotting Time)": 450.0,
    "PBF (Peripheral Blood Film)": 450.0,
    "Malaria Parasite (MP)": 200.0,
    "Blood Sugar (RBS / Fasting / 2H PP)": 800.0,
    "HbA1c": 800.0,
    "Serum Creatinine": 300.0,
    "Serum Bilirubin (Total/Direct)": 350.0,
    "SGPT (ALT)": 350.0,
    "SGOT (AST)": 350.0,
    "Serum Alkaline Phosphatase": 350.0,
    "Lipid Profile (Full)": 1000.0,
    "Serum Cholesterol": 250.0,
    "Serum Triglycerides": 350.0,
    "Serum Uric Acid": 350.0,
    "Serum Urea / BUN": 300.0,
    "Serum Electrolytes (Na, K, Cl)": 350.0
}

# গ্লোবাল ইনভয়েস কাউন্টার
invoice_counter = 1001

# ২. রসিদ জেনারেট এবং প্রিন্ট করার ফাংশন
def generate_receipt(patient_name, age, phone, selected_tests, discount_percent=0, paid_amount=0):
    global invoice_counter
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    subtotal = 0
    test_rows = []
    
    # টেস্টের মূল্য হিসাব
    for idx, test in enumerate(selected_tests, 1):
        if test in TEST_PRICES:
            price = TEST_PRICES[test]
            subtotal += price
            test_rows.append(f"{idx}. {test:<40} {price:>8.2f} TK")
            
    # ডিসকাউন্ট ও নেট বিল হিসাব
    discount_amount = (subtotal * discount_percent) / 100
    net_total = subtotal - discount_amount
    due_amount = net_total - paid_amount
    
    # মেমো/রসিদ ডিজাইন প্রিন্ট
    print("\n" + "="*55)
    print(f"{'*** আল-শেফা ডায়াগনস্টিক সেন্টার ***':^55}")
    print(f"{'ঢাকা, বাংলাদেশ | ফোন: ০১৯XXXXXXXX':^55}")
    print("="*55)
    print(f"রসিদ নং: #{invoice_counter:<15} তারিখ: {current_time}")
    print(f"রোগীর নাম: {patient_name:<15} বয়স: {age:<5} মোবাইল: {phone}")
    print("-"*55)
    print(f"{'টেস্টের নাম':<42} {'মূল্য':>10}")
    print("-"*55)
    
    for row in test_rows:
        print(row)
        
    print("-"*55)
    print(f"{'মোট মূল্য (Subtotal):':<42} {subtotal:>8.2f} TK")
    print(f"{f'ছাড় (Discount {discount_percent}%):':<42} {discount_amount:>8.2f} TK")
    print(f"{'সর্বমোট বিল (Net Total):':<42} {net_total:>8.2f} TK")
    print(f"{'নগদ পরিশোধ (Paid):':<42} {paid_amount:>8.2f} TK")
    print(f"{'বকেয়া (Due):':<42} {due_amount:>8.2f} TK")
    print("="*55)
    print(f"{'সুস্থ থাকুন, ধন্যবাদ!':^55}")
    print("="*55 + "\n")
    
    invoice_counter += 1

# ৩. সিস্টেমে ইন্টারঅ্যাক্টিভ এন্ট্রি নেওয়ার মেইন লুপ
def diagnostic_system():
    print("--- ডায়াগনস্টিক ম্যানেজমেন্ট সিস্টেমে স্বাগতম ---")
    
    while True:
        print("\n১. নতুন রোগীর রসিদ (New Receipt) কাটুন")
        print("২. টেস্টের তালিকা ও দাম দেখুন")
        print("৩. সিস্টেম বন্ধ করুন")
        choice = input("আপনার অপশনটি সিলেক্ট করুন (১/২/৩): ")
        
        if choice == "১":
            name = input("রোগীর নাম লিখুন: ")
            age = input("বয়স লিখুন: ")
            phone = input("মোবাইল নম্বর: ")
            
            # টেস্ট সিলেকশন
            selected_tests = []
            print("\nটেস্টের তালিকা থেকে নাম কপি করে পেস্ট করুন (শেষ করতে 'done' লিখুন):")
            while True:
                test_name = input("টেস্টের নাম লিখুন (বা 'done'): ").strip()
                if test_name.lower() == 'done':
                    break
                if test_name in TEST_PRICES:
                    selected_tests.append(test_name)
                    print(f"-> {test_name} যোগ করা হয়েছে।")
                else:
                    print("⚠️ দুঃখিত, এই নামের কোনো টেস্ট তালিকায় নেই! সঠিক নাম দিন।")
            
            if not selected_tests:
                print("❌ কোনো টেস্ট সিলেক্ট করা হয়নি! রসিদ বাতিল করা হলো।")
                continue
                
            # ডিসকাউন্ট ও পেমেন্ট
            try:
                discount = float(input("ডিসকাউন্ট কত %? (না থাকলে ০ দিন): ") or 0)
                paid = float(input("রোগী কত টাকা জমা দিয়েছেন?: ") or 0)
            except ValueError:
                print("⚠️ সংখ্যা ভুল লিখেছেন! ০ ধরে হিসাব করা হচ্ছে।")
                discount, paid = 0, 0
                
            # রসিদ প্রিন্ট করা
            generate_receipt(name, age, phone, selected_tests, discount, paid)
            
        elif choice == "২":
            print("\n" + "-"*45)
            print(f"{'টেস্টের নাম':<35} {'মূল্য (TK)':>8}")
            print("-"*45)
            for test, price in TEST_PRICES.items():
                print(f"{test:<35} {price:>8.2f}")
            print("-"*45)
            
        elif choice == "৩":
            print("সিস্টেম বন্ধ করা হচ্ছে। ভালো থাকুন!")
            break
        else:
            print("⚠️ ভুল অপশন চাপছেন! দয়া করে ১, ২ বা ৩ চাপুন।")

# প্রোগ্রামটি চালু করার জন্য
if __name__ == "__main__":
    diagnostic_system()
        
