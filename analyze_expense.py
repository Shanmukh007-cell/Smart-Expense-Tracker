from PIL import Image
import pytesseract
import re
from categorize_expense import categorize_expense

def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR.
    """
    try:
        img = Image.open(image_path).convert("L")
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        print(f"❌ Error while processing image: {e}")
        return ""

if __name__ == "__main__":
    image_path = "/Users/shanmukhanandudu/Desktop/test.png"   # update to your test image or pass dynamically
    print("🔍 Processing image:", image_path)

    # Extract raw text
    raw = extract_text_from_image(image_path)
    print("\n🧾 RAW OCR TEXT (repr):\n", repr(raw))

    # Clean OCR text for consistent parsing
    text = re.sub(r'\s+', ' ', raw.replace("\n", " ").replace("\r", " ")).strip()
    print("\n🧾 CLEANED OCR TEXT:\n", text)

    # Categorize and extract amount
    result = categorize_expense(text)

    print("\n✅ Expense Analysis Result:")
    print(f"Category: {result['category']}")
    print(f"Amount: ₹{result['amount']}")
