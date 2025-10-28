import re

def categorize_expense(text):
    """
    Robust expense categorizer with improved OCR number reconstruction.
    Handles cases like '7 ,076' → '7076' and ignores IDs or account digits.
    """

    categories = {
        "Food": ["mcdonald", "swiggy", "zomato", "domino", "kfc", "pizza", "restaurant", "cafe", "arabian", "biryani", "fruits", "sweet"],
        "Entertainment": ["bookmyshow", "netflix", "pvr", "hotstar", "spotify", "movie", "ticket", "district"],
        "Groceries": ["avenue", "big bazaar", "reliance", "supermarket", "grocery", "more", "ratnadeep"],
        "Clothes": ["max", "trends", "zudio", "pantaloons"],
        "Travel": ["makemytrip", "redbus"],
    }

    # ---- Step 1: Clean text ----
    text_clean = re.sub(r"[\n\r]+", " ", text)
    text_clean = re.sub(r"\s+", " ", text_clean).strip()
    lower_text = text_clean.lower()

    # ---- Step 2: Identify category ----
    found_category = "Others"
    for cat, keys in categories.items():
        if any(k in lower_text for k in keys):
            found_category = cat
            break

    # ---- Step 3: Normalize number formatting ----
    # Fix OCR issues like "7 ,076", "7, 076", "7 .076"
    text_clean = re.sub(r"(\d)[\s,\.]+(\d{3})(?!\d)", r"\1\2", text_clean)

    # ✅ Extra fix: handle OCR misreads like "7804.40" when actual was "804.40"
    text_clean = re.sub(r"(?<!\d)(7|8)(\d{3}\.\d{2})(?=\s|$)", r"\2", text_clean)

    # ---- Step 4: Extract candidate numbers ----
    num_pat = re.compile(r"[0-9]{2,7}(?:[.,][0-9]{1,2})?")
    candidates = []
    for m in num_pat.finditer(text_clean):
        token = m.group(0)
        ctx = text_clean[max(0, m.start() - 40):min(len(text_clean), m.end() + 40)].lower()

        try:
            val = float(token.replace(",", ""))
        except:
            continue

        # Only consider plausible payment values
        if not (10 <= val <= 100000):
            continue

        score = 0
        # High confidence near payment indicators
        if re.search(r"(paid|payment|successful|completed|upi|₹|rs\.?|inr)", ctx):
            score += 40
        # Low confidence near IDs or bank references
        if re.search(r"(utr|id|account|xx|ref|kotak|hdfc|axis|transaction)", ctx):
            score -= 40
        # Prefer values with comma/decimal → likely real amounts
        if "," in token or "." in token:
            score += 10

        candidates.append((val, score))

    # ---- Step 5: Pick best amount ----
    if not candidates:
        return {"category": found_category, "amount": 0.0}

    # Sort by score then value
    candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)

    # Print for debugging
    print("\n🔎 Candidate numbers (value, score):")
    for v, s in candidates:
        print(f"  {v:>8}   score={s}")

    amount = candidates[0][0]
    return {"category": found_category, "amount": round(amount, 2)}
