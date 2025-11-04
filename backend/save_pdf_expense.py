# backend/save_pdf_expense.py
import os
import pandas as pd
from datetime import datetime
from pdf_parser import extract_transactions_from_statement
from categorize_statement import categorize_statement

DATA_DIR = str((__import__("pathlib").Path(__file__).resolve().parents[1] / "data"))

def _safe_parse_date_str(x):
    if not isinstance(x, str) or not x.strip():
        return pd.NaT
    x = x.strip()
    fmts = ("%b %d, %Y", "%d %b, %Y", "%d %b %Y", "%b %d %Y", "%d %B, %Y", "%B %d, %Y")
    for fmt in fmts:
        try:
            return datetime.strptime(x, fmt)
        except Exception:
            continue
    try:
        return pd.to_datetime(x, errors="coerce")
    except:
        return pd.NaT

def append_transactions_from_pdf(pdf_path: str, csv_path: str = None, username: str = "default", ignore_duplicates: bool = True):
    """
    Extract transactions from pdf_path and append to csv_path.
    If csv_path is None, stores under data/<username>.csv
    Returns dict {'added': N, 'total': M, 'extracted': K}
    """
    if csv_path is None:
        os.makedirs(DATA_DIR, exist_ok=True)
        csv_path = os.path.join(DATA_DIR, f"{username}.csv")

    print(f"📄 Processing statement: {pdf_path}")
    df = extract_transactions_from_statement(pdf_path)
    if df.empty:
        print("⚠️ No transactions found.")
        return {"added": 0, "total": 0, "extracted": 0}

    # Ensure positive amounts only (DEBITs)
    df = df[df["Amount"].astype(float) > 0].copy()

    # categorize
    try:
        df["Category"] = df["Description"].apply(categorize_statement)
    except Exception:
        df["Category"] = "Others"

    # parse dates safely
    df["ParsedDate_dt"] = df["Date"].astype(str).apply(_safe_parse_date_str)
    df["ParsedDate"] = df["ParsedDate_dt"].apply(lambda d: d.strftime("%Y-%m-%d") if pd.notna(d) else "")

    df_out = df[["Date", "Description", "Amount", "Category", "ParsedDate"]].copy()

    # Append or create csv
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        try:
            existing = pd.read_csv(csv_path)
        except Exception:
            existing = pd.DataFrame(columns=df_out.columns)
    else:
        existing = pd.DataFrame(columns=df_out.columns)

    if ignore_duplicates and not existing.empty:
        merged = pd.concat([existing, df_out], ignore_index=True)
        before = len(merged)
        merged = merged.drop_duplicates(subset=["Date", "Amount", "Description"], keep="first")
        after = len(merged)
        added = max(0, after - len(existing))
        final = merged
    else:
        final = pd.concat([existing, df_out], ignore_index=True)
        added = len(df_out)

    final.to_csv(csv_path, index=False)
    total = len(final)
    print(f"✅ Saved {added} new transactions to {csv_path} (extracted {len(df_out)})")
    return {"added": added, "total": total, "extracted": len(df_out)}
