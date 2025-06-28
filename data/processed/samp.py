import json
import random
import string

# Files to process
INPUT_FILE = "output.jsonl"
TEMP_COUNT_FILE = "temp_count.jsonl"
TEMP_OUTPUT_FILE = "temp_output.jsonl"

# Possible aisles as letters (A to Z)
AISLES = list(string.ascii_uppercase)

def augment_item(item):
    # Add Stock_Quantity between 1 and 200
    item["Stock_Quantity"] = random.randint(1, 200)
    # Add Aisle (random letter)
    item["Aisle"] = random.choice(AISLES)
    # Add Shelf number between 1 and 10
    item["Shelf"] = random.randint(1, 10)
    # You can modify Expiring_Soon here if needed, or keep original
    return item

def process_file():
    items = []
    # Load and augment
    with open(INPUT_FILE, "r") as infile:
        for line in infile:
            item = json.loads(line)
            item = augment_item(item)
            items.append(item)

    # Save augmented items to temp_count.jsonl
    with open(TEMP_COUNT_FILE, "w") as outfile:
        for item in items:
            outfile.write(json.dumps(item) + "\n")

    # Save augmented items to temp_output.jsonl (same data for now)
    with open(TEMP_OUTPUT_FILE, "w") as outfile:
        for item in items:
            outfile.write(json.dumps(item) + "\n")

    print(f"Processed {len(items)} items, saved to {TEMP_COUNT_FILE} and {TEMP_OUTPUT_FILE}")

if __name__ == "__main__":
    process_file()

