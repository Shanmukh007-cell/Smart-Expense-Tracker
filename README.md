# Smart-Expense-Tracker
Smart Expense Tracker is a Flask-based web app that uses OCR to extract details from payment screenshots, classifies expenses into categories like Food or Groceries, and visualizes spending in a dashboard. Future upgrades include ML-based expense prediction and real-time tracking.


🧠 Features
 📸 OCR-based text extraction using Tesseract
 💰 Automatic categorization of expenses by keywords
 📊 Interactive dashboard using Flask + Chart.js
 🗂️ Stores data in CSV for easy tracking
 🔮 Future scope: Expense prediction and saving recommendations


🛠️ Tech Stack
 Layer	Technology Used
 Backend --	Python, Flask
 OCR Engine --	pytesseract, Pillow
 Frontend --	HTML, CSS, JavaScript, Chart.js
 Data Handling --	pandas, CSV
 Environment --	macOS / VS Code / virtualenv


Installation & Setup
 1. Clone the Repository
  git clone https://github.com/<your-username>/smart_expense_tracker.git
  cd smart_expense_tracker

 2. Create and Activate Virtual Environment
  python3 -m venv venv
  source venv/bin/activate   # On macOS/Linux

 3. Install Dependencies
  pip install flask pandas pillow pytesseract

 4. Run the Application
  cd backend
  python3 app.py

Now open 👉 http://127.0.0.1:5000 in your browser.


🧩 Folder Structure
smart_expense_tracker/
│
├── backend/
│   ├── app.py
│   ├── ocr_extractor.py
│   ├── analyze_expense.py
│   ├── categorize_expense.py
│   └── save_expense.py
│
├── frontend/
│   └── dashboard.html
│
└── expenses.csv


🚀 Future Enhancements
 💡 ML-based monthly expense prediction
 📲 Integration with payment APIs for real-time tracking
 🧾 Export reports as PDF or Excel
 ☁️ Deployment on Render / Railway for live access
