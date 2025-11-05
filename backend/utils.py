# backend/utils.py
import os
import csv
from pathlib import Path

# Use uploads folder (writable on Railway)
UPLOADS_DIR = Path(__file__).resolve().parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

CSV_HEADERS = ["Date", "Description", "Amount", "Category", "ParsedDate"]

def get_user_csv_path(username: str) -> str:
    """Returns full path to the user's CSV file."""
    return str(UPLOADS_DIR / f"{username}.csv")

def ensure_user_csv(username: str):
    """Creates CSV file for user if not exists, with proper headers."""
    csv_path = get_user_csv_path(username)
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(CSV_HEADERS)
    return csv_path
