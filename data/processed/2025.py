import json

# You're already in data/processed
files = ["output.jsonl", "temp_output.jsonl", "temp_count.jsonl"]

def update_year(date_str):
    """Replace year in MM/DD/YYYY with 2025."""
    parts = date_str.split("/")
    if len(parts) == 3:
        parts[2] = "2025"
    return "/".join(parts)

for filename in files:
    updated_lines = []
    
    with open(filename, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            if "Expiration_Date" in data:
                data["Expiration_Date"] = update_year(data["Expiration_Date"])
            updated_lines.append(json.dumps(data))

    with open(filename, 'w') as f:
        f.write("\n".join(updated_lines) + "\n")

print("✅ All expiration years updated to 2025.")

