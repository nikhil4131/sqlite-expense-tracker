# Expense Tracker

A full-stack personal expense tracking application built with Python, FastAPI, SQLite, HTML, CSS, and JavaScript.

Track expenses, analyze spending patterns, and manage transactions through a browser-based dashboard.

## Features

- **Expense management:** Create, view, edit, and delete expenses.
- **Dashboard statistics:** View total spending, transaction count, and highest-spending category.
- **Expense analytics:** Analyze monthly spending and category breakdowns with visual bars.
- **Month filtering:** Filter category analytics by month.
- **Input validation:** Validate positive amounts, category lengths, descriptions, and calendar dates.
- **Automated tests:** Test database operations and API behavior using pytest.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| FastAPI | REST API |
| SQLite | Persistent expense storage |
| HTML and CSS | Dashboard structure and styling |
| JavaScript | API integration and dashboard updates |
| pytest | Automated testing |

## Project Structure

```text
SQL_EXPENSE_TRACKER/
├── api/
│   └── main.py
├── dashboard/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── database.py
├── main.py
├── test_expense_tracker.py
├── test_api.py
├── expenses.db
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/nikhil4131/sqlite-expense-tracker.git
cd SQL_EXPENSE_TRACKER
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install fastapi uvicorn pytest httpx
```

### 4. Start the API

From the project root:

```bash
python -m uvicorn api.main:app --reload
```

API documentation:

http://127.0.0.1:8000/docs

### 5. Start the dashboard

Open a second terminal in the project root:

```bash
python -m http.server 5500 --directory dashboard
```

Dashboard:

http://127.0.0.1:5500/

Keep both servers running while using the application.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API health |
| GET | `/expenses` | Retrieve expenses |
| POST | `/expenses` | Create an expense |
| PUT | `/expenses/{expense_id}` | Update an expense |
| DELETE | `/expenses/{expense_id}` | Delete an expense |

Interactive API documentation is available at `/docs` while the API server is running.

## Running Tests

Run the complete test suite:

```bash
python -m pytest -v
```

The API tests use a temporary database to avoid modifying your personal expense records.

## Future Improvements

- User authentication and personal accounts
- More advanced spending charts and reports
- Pagination and search
- Deployment to a public hosting platform
- Improved accessibility and user experience

## Author

Developed as a personal full-stack project to practice Python, REST APIs, relational databases, frontend integration, and automated testing.
