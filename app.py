from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from save_expense import save_expense_to_csv

app = Flask(__name__, template_folder="../frontend")

CSV_PATH = "../expenses.csv"

@app.route("/")
def home():
    # Load expenses if file exists
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])

    # Convert to dict for frontend
    data = df.to_dict(orient="records")
    categories = df["Category"].value_counts().to_dict() if not df.empty else {}
    total_spent = df["Amount"].apply(pd.to_numeric, errors='coerce').sum() if not df.empty else 0

    return render_template("dashboard.html", data=data, categories=categories, total=round(total_spent, 2))

@app.route("/upload", methods=["POST"])
def upload():
    image = request.files["image"]
    if image:
        image_path = "../uploads/" + image.filename
        os.makedirs("../uploads", exist_ok=True)
        image.save(image_path)
        save_expense_to_csv(image_path)
        return jsonify({"message": "File processed successfully!"}), 200
    return jsonify({"error": "No image uploaded!"}), 400

if __name__ == "__main__":
    app.run(debug=True)
