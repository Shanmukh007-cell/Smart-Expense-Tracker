import csv
from datetime import datetime
from analyze_expense import extract_text_from_image, categorize_expense

def save_expense_to_csv(image_path, csv_file="../expenses.csv"):
    # 1️⃣ Run OCR and categorize
    text = extract_text_from_image(image_path)
    result = categorize_expense(text)

    # 2️⃣ Prepare expense data
    record = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Amount": result["amount"],
        "Category": result["category"],
        "Description": text.replace("\n", " ")[:150]  # short preview
    }

    # 3️⃣ Write (append) to CSV
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Date", "Amount", "Category", "Description"])
        if file.tell() == 0:  # if file is empty, write header first
            writer.writeheader()
        writer.writerow(record)

    print(f"✅ Saved: {record['Category']} | ₹{record['Amount']} | {record['Date']}")

# 🔍 Test
if __name__ == "__main__":
    image_path = "/Users/shanmukhanandudu/Desktop/test.png"
    save_expense_to_csv(image_path)
