# backend/predict_expense_from_statement.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

def prepare_monthly_data(csv_path):
    """
    Reads CSV with columns: Date, Description, Amount, Category
    Returns pivot table: rows=Month, columns=Category, values=sum of Amount
    """
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return pd.DataFrame()

    if df.empty or "Amount" not in df.columns or "Date" not in df.columns:
        return pd.DataFrame()

    # Ensure proper datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Keep DEBIT or negative entries only if applicable
    if "Type" in df.columns:
        df = df[df["Type"].str.contains("DEBIT", case=False, na=False)]

    # Extract month name
    df["Month"] = df["Date"].dt.strftime("%b")

    # Aggregate spend by month & category
    pivot = pd.pivot_table(
        df,
        index="Month",
        columns="Category",
        values="Amount",
        aggfunc="sum",
        fill_value=0
    )

    # Ensure chronological order (by actual month index)
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot = pivot.reindex([m for m in month_order if m in pivot.index])
    return pivot


def predict_next_month_expense(monthly_df):
    """
    Predicts next month’s total expense using a stable random forest + rolling mean.
    Ensures no negative values and smoother transition.
    """
    if monthly_df.empty:
        return 0.0

    # Use total spend per month
    y = monthly_df.sum(axis=1).values
    n = len(y)
    if n < 2:
        return float(y[-1])

    # Prepare supervised data (X = index, y = spend)
    X = np.arange(n).reshape(-1, 1)
    model = RandomForestRegressor(
        n_estimators=150,
        random_state=42,
        max_depth=5
    )
    model.fit(X, y)

    # Predict next index
    next_x = np.array([[n]])
    pred = model.predict(next_x)[0]

    # Rolling average smoothing
    rolling_mean = np.mean(y[-3:]) if n >= 3 else np.mean(y)
    blended = (0.6 * pred) + (0.4 * rolling_mean)

    # Prevent negatives
    final_pred = max(blended, 0)

    return round(final_pred, 2)
