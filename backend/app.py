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
from datetime import timedelta

# ----------------- FLASK APP CONFIG -----------------
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR),
    static_folder=str(FRONTEND_DIR)
)

app.secret_key = os.environ.get("FLASK_SECRET", "local-dev-secret")
app.config['SESSION_COOKIE_NAME'] = 'expense_user'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)

UPLOAD_DIR = str(BASE_DIR / "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ Ensure SQLite DB exists at startup
init_db()


# ----------------- HELPERS -----------------
def logged_in():
    return session.get("username")

def require_login(fn):
    """Decorator: only allow logged-in users."""
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
        session.clear()
        session["username"] = u
        session.permanent = False
        ensure_user_csv(u)
        return jsonify({"ok": True, "redirect": url_for("dashboard")})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/auth/register", methods=["GET"])
def auth_register():
    if logged_in():
        return redirect(url_for("dashboard"))
    return render_template("auth_register.html")


@app.route("/auth/register", methods=["POST"])
def auth_register_post():
    data = request.get_json() or request.form
    u = data.get("username", "").strip()
    p = data.get("password", "")
    e = data.get("email", "").strip()
    q1 = data.get("q1", "").strip()
    q2 = data.get("q2", "").strip()

    if not u or not p:
        return jsonify({"error": "Username & password required"}), 400

    if create_user(u, p, email=e, sec_q1=q1, sec_q2=q2):
        ensure_user_csv(u)
        session["username"] = u
        session.permanent = False
        return jsonify({"ok": True, "redirect": url_for("dashboard")})
    return jsonify({"error": "Username already exists"}), 409


@app.route("/auth/logout")
def auth_logout():
    """Clear session and logout."""
    session.clear()
    return redirect(url_for("auth_login"))


# ----------------- DASHBOARD -----------------
@app.route("/")
@require_login
def root():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@require_login
def dashboard():
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
        bar_datasets = []
        month_names = []

    return render_template("dashboard.html",
        total=total,
        predicted=predicted,
        categories=categories,
        data=df.to_dict(orient="records"),
        pie_labels=list(categories.keys()),
        pie_values=list(categories.values()),
        month_names=month_names,
        bar_datasets=bar_datasets,
        top5=(df.sort_values("Amount", ascending=False).head(5).to_dict(orient="records") if not df.empty else [])
    )


# ----------------- UPLOAD PDF -----------------
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
        result = append_transactions_from_pdf(save_path, csv_path, username=user, ignore_duplicates=True)
        return jsonify({"ok": True, "result": result})
    except Exception as e:
        print("❌ Upload failed:", e)
        print_exc()
        return jsonify({"error": str(e)}), 500


# ----------------- ADMIN DASHBOARD (PRIVATE) -----------------
@app.route("/admin/dashboard")
@require_login
def admin_dashboard():
    """Secure admin dashboard: only admin can access."""
    user = get_user_by_username(logged_in())
    if not user or not user.get("is_admin"):
        return "Forbidden", 403  # 🚫 Block non-admins

    users = list_users()
    html = [
        "<h2>👑 Admin Dashboard</h2>",
        "<p>Registered Users:</p>",
        "<table border='1' cellpadding='6' style='border-collapse:collapse;'>",
        "<tr><th>ID</th><th>Username</th><th>Email</th><th>Admin?</th></tr>"
    ]
    for u in users:
        html.append(f"<tr><td>{u['id']}</td><td>{u['username']}</td><td>{u['email'] or '-'}</td><td>{'✅' if u['is_admin'] else ''}</td></tr>")
    html.append("</table>")
    html.append("<p><a href='/dashboard'>⬅️ Back to main dashboard</a></p>")
    return "\n".join(html)


# ---------------- START SERVER ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
