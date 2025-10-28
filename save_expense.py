import csv
from datetime import datetime
from analyze_expense import extract_text_from_image
from categorize_expense import categorize_expense

def save_expense_to_csv(image_path, csv_file="../expenses.csv"):
    text = extract_text_from_image(image_path)
    result = categorize_expense(text)

    record = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Amount": result["amount"],
        "Category": result["category"],
        "Description": text[:200].replace("\n", " "),
    }

    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Amount", "Category", "Description"])
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(record)

    print(f"✅ Saved: {record['Category']} | ₹{record['Amount']} | {record['Date']}")
