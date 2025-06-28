# alerts/detect_expiring_items.py
import json

def get_expiring_items(filepath="data/processed/output.jsonl"):
    with open(filepath, "r") as f:
        return [json.loads(line) for line in f if json.loads(line).get("Expiring_Soon")]

if __name__ == "__main__":
    items = get_expiring_items()
    print(f"🚨 Found {len(items)} expiring items")

