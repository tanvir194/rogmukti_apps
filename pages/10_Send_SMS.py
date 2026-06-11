import requests

def send_patient_sms(patient_phone, patient_name, invoice_amount=None):
    """
    রুগীর মোবাইলে ডায়াগনস্টিকের নামে অটোমেটিক মেসেজ পাঠানোর ফাংশন।
    """
    # আপনার SMS গেটওয়ে প্রোভাইডারের দেওয়া API URL
    url = "https://greenweb.com.bd" # উদাহরণস্বরূপ Greenweb এর URL
    
    # গেটওয়ে থেকে পাওয়া আপনার নিজস্ব তথ্য এখানে বসাবেন
    api_token = "YOUR_API_TOKEN_SHARE" 
    sender_id = "YOUR_DIAGNOSTIC_NAME" # ডায়াগনস্টিকের অনুমোদিত নাম (Masking)
    
    # মেসেজের লেখা (আপনার পছন্দমতো পরিবর্তন করতে পারবেন)
    if invoice_amount:
        message = f"প্রিয় {patient_name}, আপনার ডায়াগনস্টিক বিল {invoice_amount} টাকা সফলভাবে পরিশোধিত হয়েছে। আমাদের ওপর আস্থা রাখার জন্য ধন্যবাদ।"
    else:
        message = f"প্রিয় {patient_name}, আমাদের ডায়াগনস্টিক সেন্টারে আপনার রেজিস্ট্রেশন সফল হয়েছে। ধন্যবাদ।"
        
    payload = {
        "token": api_token,
        "to": patient_phone,
        "message": message,
        "senderid": sender_id
    }
    
    try:
        # মেসেজ পাঠানোর রিকোয়েস্ট
        response = requests.post(url, data=payload, timeout=10)
        return response.text
    except Exception as e:
        print(f"মেসেজ পাঠাতে সমস্যা হয়েছে: {e}")
        return False
      
