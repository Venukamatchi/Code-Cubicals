import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from omnidimension import Client

# OmniDimension credentials
OMNI_API_KEY = "eCVeEkwvecsvqBCZJ_ZBQO_L65Es4u5WLduombR4qS8"
AGENT_ID = 2428
PHONE_NUMBER = "+917550041200"

# Path to your inventory dataset
DATA_PATH = "data/processed/output.jsonl"

# Initialize client
client = Client(OMNI_API_KEY)

def load_inventory():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]
    except Exception as e:
        print(f"❌ Failed to load inventory: {e}")
        return []

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%m/%d/%Y")
        return True
    except ValueError:
        return False

def group_expiries_by_month(inventory):
    now = datetime.now()
    next_month = now + timedelta(days=32)
    expiry_map = defaultdict(list)

    for item in inventory:
        try:
            date_str = item.get("Expiration_Date", "")
            if not is_valid_date(date_str):
                continue
            date = datetime.strptime(date_str, "%m/%d/%Y")
            if now <= date <= next_month:
                month_key = date.strftime("%B %Y")
                expiry_map[month_key].append(item)
        except Exception:
            continue

    return expiry_map

def generate_alert_text(monthly_expiries):
    if not monthly_expiries:
        return "Hello. This is your weekly inventory update. No items are expiring in the next two months. Thank you."

    parts = ["Hello. This is your Inventory Assistant. Here's your weekly expiry report."]
    
    for month, items in monthly_expiries.items():
        parts.append(f"\nIn {month}, the following items are expiring:")
        for itm in items[:10]:
            parts.append(
                f"- {itm['Name']} (ID: {itm['Item_ID']}) at {itm['Warehouse_Location']}, "
                f"Aisle {itm.get('Aisle', 'N/A')} Shelf {itm.get('Shelf', 'N/A')}, "
                f"Quantity left: {itm.get('Stock_Quantity', 'N/A')}"
            )
        if len(items) > 10:
            parts.append(f"...and {len(items) - 10} more items.")

    parts.append("Please review your inventory dashboard for full details. Thank you.")
    return " ".join(parts)

def send_voice_alert(agent_id, phone_number, message):
    url = "https://backend.omnidim.io/api/v1/calls/dispatch"
    headers = {
        "Authorization": f"Bearer {OMNI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "agent_id": agent_id,
        "to_number": phone_number,
        "call_context": {
            "message": message
        }
    }

    print(f"\n📞 Dispatching voice alert to {phone_number}...")
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("✅ Voice alert sent successfully.")
    else:
        print(f"❌ Failed to send voice alert ({response.status_code}): {response.text}")

def main():
    print("🔎 Processing inventory for expiry alerts...")
    inventory = load_inventory()
    if not inventory:
        print("❌ No valid inventory loaded.")
        return

    monthly_expiries = group_expiries_by_month(inventory)
    message = generate_alert_text(monthly_expiries)

    print(f"\n📤 Final voice message:\n{message[:500]}{'...' if len(message) > 500 else ''}")
    send_voice_alert(AGENT_ID, PHONE_NUMBER, message)

if __name__ == "__main__":
    main()

