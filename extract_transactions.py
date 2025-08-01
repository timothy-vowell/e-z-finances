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
