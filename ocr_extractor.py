from PIL import Image
import pytesseract

def extract_text_from_image(image_path):
    """Extracts text from image using Tesseract OCR."""
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text.strip()

if __name__ == "__main__":
    image_path = "/Users/shanmukhanandudu/Desktop/test.png"
    print(extract_text_from_image(image_path))
