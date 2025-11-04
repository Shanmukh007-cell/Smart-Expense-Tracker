# backend/categorize_statement.py
import re

# simple rule-based mapping — extend as you go
CATEGORY_KEYWORDS = {
    "Food": ["mcdonald", "kfc", "dominos", "pizza", "restaurant", "tiffins", "dosa", "canteen", "burger", "hotel", "coffee", "cafe"],
    "Entertainment": ["phoenix", "pvr", "multiplex", "movie", "bookmyshow", "ticket"],
    "Groceries": ["ratnadeep", "dmart", "supermarket", "grocery", "bigbazaar", "reliance", "kirana"],
    "Transport": ["ola", "uber", "redbus", "bus", "taxi", "auto", "fuel", "petrol", "bharat", "hpcl"],
    "Bills": ["airtel", "recharge", "phonepe", "paytm", "electricity", "bsnl", "broadband", "utility", "electric"],
    "Shopping": ["zudio", "max", "pantaloons", "amazon", "flipkart", "myntra"],
    "Health": ["clinic", "pharmacy", "medic", "hospital", "pharmacy"],
    "Others": []
}

def categorize_statement(text):
    txt = text.lower()
    # ignore wallet/gift card/credit/cashback — caller already filters DEBITs, but keep safe check
    if any(k in txt for k in ["gift card", "giftcard", "cashback", "credited", "received"]):
        return "Others"

    # person-to-person heuristics: short names, presence of "mr", "ms", "shaw", numeric-heavy names -> Others
    if re.search(r"\b(mr|ms|mrs|sri|smt|marella|raaga|venkatas?|pavan|mahamad|shaik)\b", txt):
        # still try to map some merchant names (like McDonalds -> Food)
        pass

    for cat, keys in CATEGORY_KEYWORDS.items():
        for kw in keys:
            if kw in txt:
                return cat
    # fallback: if text contains 'paid to' with a person-like token -> Others
    if re.search(r"\bpaid to [A-Za-z\s]{2,20}$", text.strip(), flags=re.IGNORECASE):
        return "Others"

    return "Others"
