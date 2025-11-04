# backend/pdf_parser.py
import fitz  # PyMuPDF
import re
import pandas as pd
from datetime import datetime

def _read_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    # normalize whitespace and NBSP
    text = text.replace("\xa0", " ")
    return text

def detect_statement_type(text):
    tx = text.lower()
    # detect PhonePe by "DEBIT" blocks & repeated "Transaction ID" style
    if "phonepe" in tx or ("debit" in tx and "transaction id" in tx and "paid to" in tx):
        return "phonepe"
    # detect GPay by "Paid to" and "UPI Transaction ID" or "Transaction statement period"
    if "upi transaction id" in tx or "transaction statement period" in tx or "google pay" in tx:
        return "gpay"
    # fallback guesses
    if "paid to" in tx and "upi transaction id" in tx:
        return "gpay"
    if "debit" in tx and "paid to" in tx:
        return "phonepe"
    return "unknown"


def _extract_from_gpay(text):
    """
    Extract "Paid to ... ₹amount" blocks from GPay statement text.
    Returns DataFrame with Date, Description, Amount.
    """
    # pattern handles date line like: 06 Sep, 2025 ... Paid to McDonalds ... ₹68.98
    pattern = re.compile(
        r"(\d{1,2}\s\w{3,9},\s20\d{2})\s+[\d:APMapm\s]*\s*(?:Paid to)\s(.+?)\s+UPI Transaction ID[:\sA-Za-z0-9\-]*.*?₹\s*([\d,]+(?:\.\d{1,2})?)",
        flags=re.IGNORECASE | re.DOTALL
    )
    matches = pattern.findall(text)
    rows = []
    for date_str, desc, amt in matches:
        try:
            val = float(amt.replace(",", ""))
        except:
            continue
        rows.append((date_str.strip(), desc.strip(), val))
    df = pd.DataFrame(rows, columns=["Date", "Description", "Amount"])
    return df


def _extract_from_phonepe(text):
    """
    Extract DEBIT entries from PhonePe-style statement text.
    We split by date lines and keep blocks with 'DEBIT' and an amount.
    """
    date_line_pat = re.compile(r"([A-Za-z]{3,9}\s\d{1,2},\s20\d{2})", flags=re.IGNORECASE)
    splits = date_line_pat.split(text)
    rows = []
    for i in range(1, len(splits), 2):
        date_token = splits[i].strip()
        block = splits[i+1]
        # consider DEBIT only (expense)
        if not re.search(r"\bDEBIT\b", block, flags=re.IGNORECASE):
            continue
        # find first ₹ amount after that date token (the transaction amount)
        amt_match = re.search(r"₹\s*([\d,]+(?:\.\d{1,2})?)", block)
        if not amt_match:
            continue
        amt = amt_match.group(1).replace(",", "")
        try:
            val = float(amt)
        except:
            continue
        # description: look for "Paid to ..." or the line after amount
        desc_match = re.search(r"(?:Paid to|Paid to:)\s*(.+?)(?:Transaction ID|UTR No|$)", block, flags=re.IGNORECASE | re.DOTALL)
        if desc_match:
            desc = desc_match.group(1).strip().splitlines()[0].strip()
        else:
            # fallback: take first non-empty line after amount
            post_amt = block[amt_match.end():].strip()
            lines = [ln.strip() for ln in post_amt.splitlines() if ln.strip()]
            desc = lines[0] if lines else "Paid"
        rows.append((date_token, desc, val))
    df = pd.DataFrame(rows, columns=["Date", "Description", "Amount"])
    return df


def extract_transactions_from_statement(pdf_path):
    """
    Auto-detect and extract DEBIT transactions.
    Returns DataFrame with columns: Date (raw), Description, Amount.
    """
    text = _read_text(pdf_path)
    stype = detect_statement_type(text)
    print(f"📄 Detected statement type: {stype}")
    if stype == "gpay":
        df = _extract_from_gpay(text)
    elif stype == "phonepe":
        df = _extract_from_phonepe(text)
    else:
        # try both and combine (safe fallback)
        df1 = _extract_from_gpay(text)
        df2 = _extract_from_phonepe(text)
        df = pd.concat([df1, df2], ignore_index=True)

    if df.empty:
        print("✅ Extracted 0 transactions from statement.")
        return df

    # normalize whitespace and trim long descriptions
    df["Description"] = df["Description"].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    print(f"✅ Extracted {len(df)} transactions from statement.")
    return df
