import os
from pathlib import Path
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for
)
from werkzeug.utils import secure_filename
from user_db import (
    init_db, create_user, verify_password,
    get_user_by_username, update_password,
    list_users, is_admin
)
from utils import ensure_user_csv
import pandas as pd


# ----------------- FLASK APP CONFIG -----------------
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# ✅ Absolute frontend paths (for Railway & local)
FRONTEND_TEMPLATES = str(ROOT_DIR / "frontend")
FRONTEND_STATIC = str(ROOT_DIR / "frontend")

# Print these to verify once during Railway logs
print("📂 FRONTEND_TEMPLATES =", FRONTEND_TEMPLATES)
print("📂 FRONTEND_STATIC =", FRONTEND_STATIC)
print("📂 Current Working Dir =", os.getcwd())

# ✅ Initialize Flask with absolute template/static dirs
app = Flask(
    __name__,
    template_folder=FRONTEND_TEMPLATES,
    static_folder=FRONTEND_STATIC
)

app.secret_key = os.environ.get("FLASK_SECRET", "local-dev-secret")
app.config["SESSION_COOKIE_NAME"] = "expense_user"

UPLOAD_DIR = str(BASE_DIR / "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ Ensure SQLite DB exists at startup
init_db()


# ----------------- HELPERS -----------------
def logged_in():
    return session.get("username")


def require_login(fn):
    """Decorator to require login for routes."""
    def wrapper(*a, **kw):
        if not logged_in():
            return redirect(url_for("auth_login"))
        return fn(*a, **kw)
    wrapper.__name__ = fn.__name__
    return wrapper


# ----------------- AUTH ROUTES -----------------
@app.route("/auth/login", methods=["GET"])
def auth_login():
    if logged_in():
        return redirect(url_for("dashboard"))
    return render_template("auth_login.html")


@app.route("/auth/login", methods=["POST"])
def auth_login_post():
    data = request.form or request.json or {}
    u = data.get("username", "").strip()
    p = data.get("password", "")

    if verify_password(u, p):
        session["username"] = u
        ensure_user_csv(u)
        return jsonify({"ok": True, "redirect": url_for("dashboard")})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/auth/register", methods=["GET"])
def auth_register():
    """Render the registration page."""
    if logged_in():
        return redirect(url_for("dashboard"))
    return render_template("auth_register.html")


@app.route("/auth/register", methods=["POST"])
def auth_register_post():
    """Handle user registration form submission."""
    data = request.form or request.json or {}
    u = data.get("username", "").strip()
    p = data.get("password", "")
    e = data.get("email", "").strip()
    q1 = data.get("sec_q1", "").strip()
    q2 = data.get("sec_q2", "").strip()

    if not u or not p:
        return jsonify({"error": "Username & password required"}), 400

    if create_user(u, p, email=e, sec_q1=q1, sec_q2=q2):
        ensure_user_csv(u)
        session["username"] = u
        return jsonify({"ok": True, "redirect": url_for("dashboard")})
    return jsonify({"error": "Username already exists"}), 409


# ----------------- DASHBOARD -----------------
@app.route("/")
@require_login
def root():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@require_login
def dashboard():
    """Main dashboard: loads user data and visualizations."""
    from predict_expense_from_statement import (
        prepare_monthly_data,
        predict_next_month_expense
    )

    user = logged_in()
    csv_path = ensure_user_csv(user)

    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame()

    total = round(df["Amount"].sum(), 2) if not df.empty else 0.0
    categories = df["Category"].value_counts().to_dict() if not df.empty else {}

    monthly = prepare_monthly_data(csv_path) if not df.empty else pd.DataFrame()
    predicted = predict_next_month_expense(monthly) if not monthly.empty else 0.0

    # ✅ Grouped bar datasets
    if not monthly.empty:
        bar_datasets = [
            {"label": cat, "data": monthly[cat].tolist()}
            for cat in monthly.columns
        ]
        month_names = monthly.index.tolist()
    else:
        bar_datasets, month_names = [], []

    return render_template(
        "dashboard.html",
        total=total,
        predicted=predicted,
        categories=categories,
        data=df.to_dict(orient="records"),
        pie_labels=list(categories.keys()),
        pie_values=list(categories.values()),
        month_names=month_names,
        bar_datasets=bar_datasets,
        top5=(
            df.sort_values("Amount", ascending=False)
            .head(5)
            .to_dict(orient="records")
            if not df.empty
            else []
        ),
    )


# ----------------- PDF UPLOAD -----------------
@app.route("/upload", methods=["POST"])
@require_login
def upload_pdf():
    from traceback import print_exc

    pdf = request.files.get("pdf")
    if not pdf:
        return jsonify({"error": "No PDF uploaded"}), 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    fname = secure_filename(pdf.filename)
    save_path = os.path.join(UPLOAD_DIR, fname)
    pdf.save(save_path)

    user = logged_in()
    csv_path = ensure_user_csv(user)

    try:
        from save_pdf_expense import append_transactions_from_pdf

        result = append_transactions_from_pdf(
            save_path, csv_path, username=user, ignore_duplicates=True
        )
        print(f"✅ Upload result: {result}")
        return jsonify({"ok": True, "result": result})
    except Exception as e:
        print("❌ Upload failed:", e)
        print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------- ADMIN ROUTE -----------------
@app.route("/admin/users")
@require_login
def admin_users():
    """Admin-only view to list all users."""
    u = get_user_by_username(logged_in())
    if not u or not u.get("is_admin"):
        return "Forbidden", 403
    return jsonify(list_users())


# ---------------- DEBUG PATH ROUTE ----------------
@app.route("/debug-paths")
def debug_paths():
    """Optional: to check template/static path correctness."""
    return jsonify({
        "cwd": os.getcwd(),
        "template_folder": app.template_folder,
        "static_folder": app.static_folder,
        "frontend_exists": os.path.exists(app.template_folder),
        "auth_register_exists": os.path.exists(os.path.join(app.template_folder, "auth_register.html")),
    })


# ---------------- START SERVER ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # ✅ Railway dynamic port
    app.run(host="0.0.0.0", port=port)
