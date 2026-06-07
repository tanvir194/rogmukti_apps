import datetime

# List of available tests and their prices
TEST_PRICES = {
    "cbc": 400,
    "blood sugar": 150,
    "lipid profile": 1200,
    "creatinine": 300,
    "urine re": 250,
    "x-ray chest": 600,
    "ultrasonography": 1500,
    "ecg": 400
}

# Starting invoice number
invoice_counter = 1001
def generate_receipt(patient_name, age, phone, selected_tests, discount_percent=0, paid_amount=0):
    global invoice_counter
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    subtotal = 0
    test_rows = []
    
    # Calculate test prices
    for idx, test_name in enumerate(selected_tests, 1):
        if test_name in TEST_PRICES:
            price = TEST_PRICES[test_name]
            subtotal += price
            test_rows.append(f"{idx}. {test_name.upper():<25} : {price:>6} USD")
            
    # Calculate discount and totals
    discount_amount = (subtotal * discount_percent) / 100
    net_total = subtotal - discount_amount
    due_amount = net_total - paid_amount
    
    # Print receipt layout
    print("\n" + "="*50)
    print(f"{'*** AL-MADINA DIAGNOSTIC CENTER ***':^50}")
    print(f"{'Dhaka, Bangladesh | Phone: 01XXXXXXXXX':^50}")
    print("="*50)
    print(f"Invoice No : #{invoice_counter:<14} Date: {current_time}")
    print(f"Patient Name: {patient_name:<14} Age : {age:<5} Phone: {phone}")
    print("-"*50)
    print(f"{'Test Description':<28} : {'Price':>9}")
    print("-"*50)
    
    for row in test_rows:
        print(row)
        
    print("-"*50)
    print(f"{'Subtotal':<27} : {subtotal:>6}.00 USD")
    print(f"{'Discount (' + str(discount_percent) + '%)':<27} : {discount_amount:>6}.00 USD")
    print(f"{'Net Total':<27} : {net_total:>6}.00 USD")
    print(f"{'Paid Amount':<27} : {paid_amount:>6}.00 USD")
    print(f"{'Due Amount':<27} : {max(0, due_amount):>6}.00 USD")
    print("="*50)
    print(f"{'*** Stay Healthy, Live Well ***':^50}")
    print("="*50 + "\n")
    
    invoice_counter += 1
    def diagnostic_system():
    while True:
        print("\n--- DIAGNOSTIC MANAGEMENT SYSTEM ---")
        print("1. Create New Receipt")
        print("2. View Test Menu & Prices")
        print("3. Exit System")
        
        choice = input("Select an option (1/2/3): ").strip()
        
        if choice == "1":
            print("\n--- Enter Patient Information ---")
            name = input("Patient Name: ").strip()
            age = input("Patient Age: ").strip()
            phone = input("Phone Number: ").strip()
            
            # Test Selection Loop
            selected_tests = []
            print("\nEnter test names from the menu. Type 'done' to finish.")
            print("Available tests:", ", ".join(TEST_PRICES.keys()))
            
            while True:
                test_name = input("Enter Test Name (or 'done'): ").strip().lower()
                
                if test_name == 'done':
                    break
                    
                if test_name in TEST_PRICES:
                    if test_name not in selected_tests:
                        selected_tests.append(test_name)
                        print(f"-> {test_name.upper()} has been added.")
                    else:
                        print("⚠ This test has already been added.")
                else:
                    print("⚠ Invalid test name! Please check the menu and try again.")
            
            # If no tests were selected
            if not selected_tests:
                print("❌ No tests selected! Receipt creation canceled.")
                continue
                
            # Inputs for Discount and Payment
            try:
                discount = float(input("\nEnter Discount % (Enter 0 if none): ") or 0)
                paid = float(input("Enter Paid Amount (Enter 0 if none): ") or 0)
            except ValueError:
                print("⚠ Invalid input! Setting discount and paid amount to 0.")
                discount, paid = 0, 0
                
            # Generate the final receipt
            generate_receipt(name, age, phone, selected_tests, discount, paid)
            
        elif choice == "2":
            print("\n" + "-"*40)
            print(f"{'Test Name':<25} | {'Price (USD)':>12}")
            print("-"*40)
            for test, price in TEST_PRICES.items():
                print(f"{test.upper():<25} | {price:>12} USD")
            print("-"*40)
            
        elif choice == "3":
            print("\nShutting down the system. Thank you!")
            break
        else:
            print("❌ Invalid choice! Please select option 1, 2, or 3.")
        # Program entry point
if __name__ == "__main__":
    diagnostic_system()
    
