'''
import pdfplumber
import pandas as pd
import re

# === CONFIGURATION ===
PDF_PATH = "2025-07-03.pdf"
OUTPUT_PATH = "parsed_transactions.xlsx"

# === CATEGORY RULES ===
def categorize(desc):
    desc = desc.lower()
    if "walmart" in desc or "supercenter" in desc:
        return "Groceries"
    elif "food rite" in desc or "365 market" in desc:
        return "Snacks/Groceries"
    elif "onlyfans" in desc:
        return "Subscriptions"
    elif "amazon" in desc:
        return "Shopping"
    elif "murphy" in desc or "gas" in desc:
        return "Gas"
    elif "tracfone" in desc:
        return "Phone"
    elif "gibson electric" in desc or "gibsonconnect" in desc:
        return "Utilities"
    elif "water" in desc:
        return "Utilities"
    elif "dollar general" in desc:
        return "Household"
    else:
        return "Other"

# === STEP 1: Extract text lines from PDF ===
def extract_lines(pdf_path):
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for line in text.split('\n'):
                if re.match(r"\d{2}/\d{2} \d{2}/\d{2} \d{4}", line):
                    lines.append(line.strip())
    return lines

# === STEP 2: Parse each line into structured fields ===
def parse_line(line):
    match = re.match(r"(\d{2}/\d{2}) (\d{2}/\d{2}) (\d{4}) (.+?) \$([0-9]+\.[0-9]{2})", line)
    if match:
        post_date, trans_date, card, desc, amount = match.groups()
        return {
            "Post Date": post_date,
            "Trans Date": trans_date,
            "Card": card,
            "Description": desc.strip(),
            "Amount": float(amount),
            "Category": categorize(desc)
        }
    return None

# === STEP 3: Run everything ===
def main():
    print("📥 Reading transactions from PDF...")
    raw_lines = extract_lines(PDF_PATH)
    parsed = [parse_line(line) for line in raw_lines]
    parsed = [p for p in parsed if p is not None]

    if not parsed:
        print("❌ No transactions were parsed. Check format.")
        return

    df = pd.DataFrame(parsed)
    df.to_excel(OUTPUT_PATH, index=False)
    print(f"✅ Done! Parsed {len(df)} transactions → {OUTPUT_PATH}")

if __name__ == "__main__":
    main()



import pdfplumber
import pandas as pd
import re
import json
from pathlib import Path
import shutil

PDF_DIR = Path("pdfs")
PROCESSED_DIR = Path("processed")
RULES_PATH = Path("categorization_rules.json")
OUTPUT_FILE = Path("parsed/parsed_transactions.xlsx")

PROCESSED_DIR.mkdir(exist_ok=True)

# Load categorization rules from JSON
with open(RULES_PATH) as f:
    rules = json.load(f)

def categorize(description):
    desc = description.lower()
    for keyword, category in rules.items():
        if keyword.lower() in desc:
            return category
    return "Uncategorized"

def extract_transactions_from_pdf(pdf_path):
    transactions = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.splitlines()
            for line in lines:
                # Match typical transaction line: MM/DD optional MM/DD + description + $amount
                match = re.match(r"\d{2}/\d{2}\s+\d{2}/\d{2}\s+(.*)\s+\$(\d+\.\d{2})", line)
                if match:
                    raw_desc = match.group(1).strip()
                    amount = float(match.group(2))
                    category = categorize(raw_desc)
                    transactions.append({
                        "Description": raw_desc,
                        "Amount": amount,
                        "Category": category,
                        "Source File": pdf_path.name
                    })
    return transactions

# Aggregate all parsed transactions
all_transactions = []
for pdf_file in PDF_DIR.glob("*.pdf"):
    txns = extract_transactions_from_pdf(pdf_file)
    all_transactions.extend(txns)
    shutil.move(str(pdf_file), PROCESSED_DIR / pdf_file.name)

# Save to a single Excel file
if all_transactions:
    df = pd.DataFrame(all_transactions)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Saved {len(df)} transactions to {OUTPUT_FILE}")
else:
    print("⚠️ No transactions found.")
'''



import pdfplumber
import pandas as pd
import re
import json
from pathlib import Path
import shutil

# === Paths ===
PDF_DIR = Path("pdfs")
PROCESSED_DIR = Path("processed")
OUTPUT_DIR = Path("parsed-transactions")
RULES_PATH = Path("categories.json")
OUTPUT_FILE = OUTPUT_DIR / "parsed_transactions.xlsx"

# Ensure required folders exist
PROCESSED_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# === Load categorization rules ===
with open(RULES_PATH) as f:
    rules = json.load(f)

# === Normalize description ===
def normalize(text):
    text = text.lower()
    return re.sub(r"[^a-z0-9 ]", "", text)

# === Categorization logic ===
def categorize(description):
    norm_desc = normalize(description)
    for category, keywords in rules.items():
        for keyword in keywords:
            if keyword in norm_desc:
                return category
    return "Uncategorized"

# === Extract transactions from one PDF ===
def extract_transactions_from_pdf(pdf_path):
    transactions = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.splitlines()
            for line in lines:
                # Match: MM/DD MM/DD description $amount
                match = re.match(r"(\d{2}/\d{2})\s+\d{2}/\d{2}\s+(.*)\s+\$(\d+\.\d{2})", line)
                if match:
                    date = match.group(1)
                    raw_desc = match.group(2).strip()
                    amount = float(match.group(3))
                    category = categorize(raw_desc)
                    transactions.append({
                        "Date": date,
                        "Description": raw_desc,
                        "Amount": amount,
                        "Category": category,
                        "Source File": pdf_path.name
                    })

    return transactions

# === Main parsing loop ===
all_transactions = []
for pdf_file in PDF_DIR.glob("*.pdf"):
    txns = extract_transactions_from_pdf(pdf_file)
    all_transactions.extend(txns)
    shutil.move(str(pdf_file), PROCESSED_DIR / pdf_file.name)

# === Save results ===
if all_transactions:
    df = pd.DataFrame(all_transactions)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Saved {len(df)} transactions to {OUTPUT_FILE}")
else:
    print("⚠️ No transactions found.")
