
import pathway as pw
import pandas as pd
from datetime import datetime
import os
import logging
import json
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Define the schema to match all CSV columns
class InputSchema(pw.Schema):
    Product_ID: str
    Product_Name: str
    Catagory: str
    Supplier_ID: str
    Supplier_Name: str
    Stock_Quantity: int
    Reorder_Level: int
    Reorder_Quantity: int
    Unit_Price: str
    Date_Received: str
    Last_Order_Date: str
    Expiration_Date: str
    Warehouse_Location: str
    Sales_Volume: int
    Inventory_Turnover_Rate: int
    Status: str

# Output paths
OUTPUT_PATH = "data/processed/output.jsonl"
TEMP_OUTPUT_PATH = "data/processed/temp_output.jsonl"
TEMP_COUNT_PATH = "data/processed/temp_count.jsonl"
CSV_PATH = "data/uploads/Grocery_Inventory_and_Sales_Dataset.csv"

# Verify file existence
if not os.path.exists(CSV_PATH):
    logging.error(f"CSV file not found at {CSV_PATH}")
    raise FileNotFoundError(f"CSV file not found at {CSV_PATH}")

# Step 1: Read CSV from the specific file
try:
    csv_input = pw.io.csv.read(
        CSV_PATH,
        schema=InputSchema,
        mode="static",
        autocommit_duration_ms=1000,
    )
    logging.info(f"Successfully read CSV from {CSV_PATH}")
except Exception as e:
    logging.error(f"Failed to read CSV: {str(e)}")
    raise

# Step 2: Log the number of rows read
def log_row_count(table):
    try:
        count_table = table.reduce(count=pw.reducers.count())
        pw.io.jsonlines.write(count_table.select(count=pw.this.count), TEMP_COUNT_PATH)
        logging.info(f"Row count written to {TEMP_COUNT_PATH}. Check file for details.")
    except Exception as e:
        logging.warning(f"Failed to count rows: {str(e)}. Proceeding without count.")
    return table

csv_input = log_row_count(csv_input)

# Step 3: Select and rename relevant columns
filtered_table = csv_input.select(
    Item_ID=pw.this.Product_ID,
    Name=pw.this.Product_Name,
    Expiration_Date=pw.this.Expiration_Date,
    Warehouse_Location=pw.this.Warehouse_Location,
)

# Step 4: Add Expiring_Soon flag
def compute_expiring_soon(exp_date_str):
    try:
        exp_date = pd.to_datetime(exp_date_str, format="%m/%d/%Y", errors="coerce")
        today = pd.Timestamp("2025-06-28")  # Hardcode date for consistency
        if pd.notnull(exp_date):
            days_diff = (exp_date - today).days
            logging.debug(f"Date {exp_date_str}: {days_diff} days from {today}")
            return 0 <= days_diff <= 7
        logging.warning(f"Invalid date '{exp_date_str}'")
        return False
    except Exception as e:
        logging.warning(f"Failed to parse date '{exp_date_str}': {str(e)}")
        return False

cleaned_table = filtered_table.with_columns(
    Expiring_Soon=pw.apply(compute_expiring_soon, pw.this.Expiration_Date)
)

# Step 5: Write to temporary output and post-process
try:
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    output_table = cleaned_table.select(
        Item_ID=pw.this.Item_ID,
        Name=pw.this.Name,
        Expiration_Date=pw.this.Expiration_Date,
        Warehouse_Location=pw.this.Warehouse_Location,
        Expiring_Soon=pw.this.Expiring_Soon
    )
    # Write to temporary JSONL
    pw.io.jsonlines.write(output_table, TEMP_OUTPUT_PATH)
    logging.info(f"Wrote temporary output to {TEMP_OUTPUT_PATH}")

    # Run the pipeline to ensure temp output is written
    logging.info("Running Pathway pipeline for temporary output")
    pw.run()
    logging.info("Pipeline execution completed for temporary output")

    # Wait briefly to ensure file is flushed
    time.sleep(2)

    # Post-process to create clean JSONL
    desired_fields = ["Item_ID", "Name", "Expiration_Date", "Warehouse_Location", "Expiring_Soon"]
    try:
        with open(TEMP_OUTPUT_PATH, "r", encoding="utf-8") as temp_f, open(OUTPUT_PATH, "w", encoding="utf-8") as out_f:
            for line in temp_f:
                try:
                    data = json.loads(line.strip())
                    cleaned_data = {k: data[k] for k in desired_fields if k in data}
                    json.dump(cleaned_data, out_f)
                    out_f.write("\n")
                except json.JSONDecodeError as e:
                    logging.warning(f"Failed to parse temp JSON line: {line.strip()}. Error: {str(e)}")
                    continue
        logging.info(f"Cleaned and wrote final output to {OUTPUT_PATH}")
    except FileNotFoundError:
        logging.warning(f"Temporary file {TEMP_OUTPUT_PATH} not found. Falling back to direct write.")
        pw.io.jsonlines.write(output_table, OUTPUT_PATH)
        logging.info(f"Fell back to direct write to {OUTPUT_PATH}")
        pw.run()  # Run again for fallback
        logging.info("Pipeline execution completed for fallback output")
except Exception as e:
    logging.error(f"Failed to write output: {str(e)}")
    raise

