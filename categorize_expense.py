import re

# Sample extracted text (later you'll get this from OCR)
text = """
To McDonalds
₹68.98
Payment Completed
27 Sept 2025, 8:19 pm
Canara Bank 4454
"""

# Expense category keywords
categories = {
    "Food": ["mcdonald", "swiggy", "zomato", "domino", "kfc", "pizza"],
    "Entertainment": ["bookmyshow", "netflix", "pvr", "hotstar", "spotify"],
    "Groceries": ["dmart", "big bazaar", "reliance", "more", "supermarket", "grocery"],
}

# Normalize text
lower_text = text.lower()

# Find matching category
found_category = "Others"
for category, keywords in categories.items():
    if any(word in lower_text for word in keywords):
        found_category = category
        break

# Extract amount
amount_match = re.search(r"₹\s?([\d,]+\.\d{1,2})", text)
amount = amount_match.group(1) if amount_match else "Unknown"

# Display result
print(f"Extracted Amount: ₹{amount}")
print(f"Category: {found_category}")
