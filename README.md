# 📊 Smart Expense Tracker  

![Python](https://img.shields.io/badge/Python-3.10-yellow?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-2.3-blue?style=flat-square)
![Machine Learning](https://img.shields.io/badge/ML-Expense%20Prediction-orange?style=flat-square)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

> An intelligent expense tracking web app that extracts and categorizes transactions from **bank statements (PDF)**, visualizes insights with **charts**, and predicts **next month’s expenses** — built with Flask, Pandas, and lightweight ML.

---

## 🚀 Overview  

Smart Expense Tracker simplifies the way you manage finances by:
- Uploading your **bank/PDF statements**
- Automatically extracting transaction data using OCR and parsing logic
- Categorizing each transaction into **Food, Shopping, Bills, etc.**
- Visualizing your spend pattern through **interactive charts**
- Predicting **next month’s total expenses** using linear regression  
- Supporting **multiple users**, each with a private expense file

---

## ✨ Key Features  

| Feature | Description |
|----------|-------------|
| 🔐 **Secure Login & Registration** | Encrypted passwords with Flask sessions |
| 📂 **Smart PDF Upload** | Parses and updates your expense data automatically |
| 📈 **Interactive Dashboard** | Displays total spending, top categories, and charts |
| 🧠 **Expense Prediction Model** | Forecasts upcoming month expenses |
| 🌗 **Light/Dark Mode** | User-friendly UI with theme toggle |
| 👥 **User Isolation** | Each user has their own CSV dataset |
| 🧩 **Admin Panel** | Admin can view all registered users |
| 🧾 **Data Persistence** | Uses SQLite for users, CSVs for statements |

---

## 🖼️ UI Preview  

> (You can replace these placeholders with real screenshots later)

| Login Page | Dashboard (Dark Mode) |
|-------------|----------------------|
| ![Login](https://via.placeholder.com/400x250?text=Login+Page) | ![Dashboard](https://via.placeholder.com/400x250?text=Dashboard+View) |

---

## ⚙️ Installation & Setup  

### 1️⃣ Clone Repository  

git clone https://github.com/Shanmukh007-cell/Smart-Expense-Tracker.git
cd Smart-Expense-Tracker

### 2️⃣ Create Virtual Environment
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Setup Environment Variables
Create a .env file in the project root (not inside backend):
FLASK_SECRET=replace-this-with-a-random-string

5️⃣ Run Locally
cd backend
python3 app.py
Open: 👉 http://127.0.0.1:5001

🧠 Tech Stack
Layer	Technology
Frontend	HTML, CSS, JS (Vanilla + Chart.js)
Backend	Flask (Python)
Database	SQLite3
Prediction	Pandas + Scikit-learn Linear Regression
Deployment	Railway.app
Version Control	GitHub

🧮 Folder Structure
Smart-Expense-Tracker/
│
├── backend/
│   ├── app.py
│   ├── user_db.py
│   ├── utils.py
│   ├── predict_expense_from_statement.py
│   ├── save_pdf_expense.py
│   ├── uploads/
│   ├── data/
│   └── requirements.txt
│
├── frontend/
│   ├── dashboard.html
│   ├── auth_login.html
│   ├── auth_register.html
│   ├── static/
│
├── .env.example
├── Procfile
├── requirements.txt
└── README.md

🌍 Deployment (Railway)

Push code to GitHub ✅

Go to Railway Dashboard

Click New Project → Deploy from GitHub

Select this repo

Add Railway environment variable:

FLASK_SECRET=your-random-secret-here


Deploy — Railway auto-detects Flask 🎉

🛠️ Future Roadmap
Feature	Status	Notes
Email verification	⏳ Planned	Gmail API
Mobile responsive UI	✅ Done	
Multi-user CSV isolation	✅ Done	
Admin dashboard (user list)	✅ Done	
Cloud export (Google Sheets)	⏳ Planned	
AI-based auto category detection	🚧 In research	

👨‍💻 Developer
Shanmukh Marella
📧 anandhhmarella530@gmail.com
🌐 GitHub: https://github.com/Shanmukh007-cell

📄 License
This project is licensed under the MIT License — you are free to use, modify, and distribute.
MIT © 2025 Shanmukh Marella

