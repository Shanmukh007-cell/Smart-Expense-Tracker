from PIL import Image
import pytesseract
import re

# ===== Step 1: OCR Extraction =====
def extract_text_from_image(image_path):
    """
    Extracts text from an image using Tesseract OCR.
    """
    try:
        img = Image.open(image_path)
        img = img.convert("L")  # convert to grayscale for better accuracy
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        print(f"❌ Error while processing image: {e}")
        return ""


# ===== Step 2: Expense Categorization =====
def categorize_expense(text):
    """
    Categorizes expense based on extracted text content.
    """
    categories = {
        "Food": ["mcdonald", "swiggy", "zomato", "domino", "kfc", "pizza", "restaurant", "cafe"],
        "Entertainment": ["bookmyshow", "netflix", "pvr", "hotstar", "spotify", "movie"],
        "Groceries": ["dmart", "big bazaar", "reliance", "supermarket", "grocery", "more"],
    }

    lower_text = text.lower()
    found_category = "Others"

    for category, keywords in categories.items():
        if any(word in lower_text for word in keywords):
            found_category = category
            break

    # Extract amount (₹ or Rs)
    amount_match = re.search(r"(?:₹|rs\.?|%?)\s?([\d,]+(?:\.\d{1,2})?)", text, re.IGNORECASE)
    amount = amount_match.group(1) if amount_match else "Unknown"

    return {"category": found_category, "amount": amount}


# ===== Step 3: Full Pipeline =====
if __name__ == "__main__":
    image_path = "/Users/shanmukhanandudu/Desktop/test.png"   # ✅ update this path
    print("🔍 Processing image...")

    text = extract_text_from_image(image_path)
    print("\n🧾 Extracted Text:\n", text)

    result = categorize_expense(text)
    print("\n✅ Expense Analysis Result:")
    print(f"Category: {result['category']}")
    print(f"Amount: ₹{result['amount']}")
