# alerts/omni_voice_alert.py

import requests
import json

# 🔐 Hardcoded Omni API key (for demo purposes ONLY)
API_KEY = "JZPaq_oYAu30ggdL7dL1ApxaxtvzukFYrVY8xoyl9cg"
OMNI_API_URL = "https://backend.omnidim.io/api/v1/voice/call"

# 📞 Replace with real warehouse manager phone number (include country code)
WAREHOUSE_MANAGER_PHONE = "+919080221016"  # Change this for your test/demo

def send_voice_alert(item):
    message = f"📦 Alert! {item['Name']} is expiring on {item['Expiration_Date']} at {item['Warehouse_Location']}."
    
    payload = {
        "phone": WAREHOUSE_MANAGER_PHONE,
        "text": message,
        "speaker": "female",     # or "male"
        "voice": "en-US"         # en-IN also works
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(OMNI_API_URL, headers=headers, data=json.dumps(payload))
        if res.ok:
            print(f"📞 Alert sent: {item['Name']} expiring on {item['Expiration_Date']}")
        else:
            print(f"❌ Error: {res.status_code} - {res.text}")
    except Exception as e:
        print("❌ Failed to send voice alert:", e)

