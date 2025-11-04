# backend/create_admin.py
from user_db import init_db, create_user, get_user_by_username
from utils import ensure_user_csv

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

print("🔄 Initializing DB...")
init_db()

print(f"👤 Checking admin user '{ADMIN_USERNAME}'...")

existing = get_user_by_username(ADMIN_USERNAME)
if existing:
    print("✅ Admin already exists — skipping DB insert")
else:
    ok = create_user(
        ADMIN_USERNAME,
        ADMIN_PASSWORD,
        email="admin@local",
        sec_q1=None,
        sec_q2=None,
        is_admin=1
    )
    if ok:
        print(f"✅ Admin created: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    else:
        print("❌ Failed to create admin user!")

# Always ensure admin CSV exists
ensure_user_csv(ADMIN_USERNAME)
print("📄 Ensured admin CSV file exists.")
