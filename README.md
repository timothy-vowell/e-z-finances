#  PDF Credit Card Statement Parser

This project automates the extraction of credit card transaction data from PDF statements.  
It parses each transaction line into structured fields and exports a categorized `.xlsx` file.

---

##  What It Does

-  Reads PDF statements from the `pdfs/` folder
-  Extracts and parses each transaction line:
  - Post Date
  - Transaction Date
  - Last 4 digits of card
  - Description
  - Amount
-  Categorizes each transaction based on keywords (e.g. "Walmart" → Groceries)
-  Outputs clean Excel files into the `parsed/` folder

---

##  Folder Structure

chatgpt-projects/
├── pdfs/ # Raw input PDFs
├── parsed/ # Output Excel files
├── extract_transactions.py # Main Python script
└── README.md # This file

##  How to Run

### 1. Install dependencies
```bash
pip3 install pdfplumber pandas openpyxl
```

### 2. Run

python3 extract_transactions.py <pdf-file.pdf> <parsed-file.xlsx>
