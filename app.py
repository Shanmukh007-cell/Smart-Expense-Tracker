from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from save_expense import save_expense_to_csv
from predict_expense import prepare_data, predict_next_month

# Initialize Flask
app = Flask(__name__, template_folder="../frontend")

# Path to your CSV file
CSV_PATH = "../expenses.csv"

@app.route("/")
def home():
    """Render main dashboard with current stats and prediction."""
    try:
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH)
        else:
            df = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])
    except Exception as e:
        print(f"⚠️ Error reading CSV: {e}")
        df = pd.DataFrame(columns=["Date", "Amount", "Category", "Description"])

    # Compute summary data
    data = df.to_dict(orient="records")
    categories = df["Category"].value_counts().to_dict() if not df.empty else {}
    total_spent = df["Amount"].apply(pd.to_numeric, errors="coerce").sum() if not df.empty else 0

    # Generate next month prediction
    if not df.empty and len(df) > 2:
        try:
            prepared_df = prepare_data(CSV_PATH)
            next_month_pred = predict_next_month(prepared_df)
        except Exception as e:
            print(f"⚠️ Prediction error: {e}")
            next_month_pred = 0.0
    else:
        next_month_pred = 0.0

    # Render frontend dashboard
    return render_template(
        "dashboard.html",
        data=data,
        categories=categories,
        total=round(total_spent, 2),
        predicted=round(next_month_pred, 2)
    )


@app.route("/upload", methods=["POST"])
def upload():
    """Handle image uploads and save extracted expense data."""
    image = request.files.get("image")
    if not image:
        return jsonify({"error": "No image uploaded!"}), 400

    os.makedirs("../uploads", exist_ok=True)
    image_path = f"../uploads/{image.filename}"
    image.save(image_path)

    try:
        save_expense_to_csv(image_path)
        return jsonify({"message": "File processed successfully!"}), 200
    except Exception as e:
        print(f"❌ Error saving expense: {e}")
        return jsonify({"error": "Failed to process file."}), 500


@app.route("/predict")
def predict_expense():
    """Optional API route to fetch next month’s expense prediction."""
    try:
        df = prepare_data(CSV_PATH)
        next_month = predict_next_month(df)
        return jsonify({"predicted_expense": round(next_month, 2)})
    except Exception as e:
        print(f"⚠️ Prediction API error: {e}")
        return jsonify({"predicted_expense": 0.0})


if __name__ == "__main__":
    app.run(debug=True)
