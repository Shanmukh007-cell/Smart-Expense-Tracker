from PIL import Image
import pytesseract

def extract_text_from_image(image_path):
    """
    Extracts text from the given image using Tesseract OCR.
    """
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text.strip()

# Optional: Run this file directly to test OCR
if __name__ == "__main__":
    image_path = "/Users/shanmukhanandudu/Desktop/test.png"  # ✅ your image path
    extracted_text = extract_text_from_image(image_path)
    print("Extracted Text:\n")
    print(extracted_text)
