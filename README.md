# SQLite Expense Tracker

A command-line expense tracking application built with Python and SQLite. It allows users to record, view, update, delete, and analyze their expenses through a menu-driven interface.

## Features

- **Add Expenses:** Record an amount, category, description, and date.
- **View Expenses:** Display saved expenses.
- **Update Expenses:** Modify existing expense records.
- **Delete Expenses:** Remove expenses with an ID-based selection.
- **Spending Summary:** Calculate total expenses and category-wise spending.
- **Filter by Date:** View expenses within a specified date range.
- **Input Validation:** Handle invalid amounts, dates, and expense IDs.
- **SQLite Database:** Store expense records persistently.
- **Unit Testing:** Test database operations using Python's `unittest` framework and temporary databases.

## Technologies Used

- Python
- SQLite
- `unittest`
- `tempfile`

## Project Structure

```text
SQL_EXPENSE_TRACKER/
├── main.py
├── database.py
├── test_expense_tracker.py
├── expenses.db
└── README.md
```

`expenses.db` is created automatically when the application initializes its database. Do not commit personal expense data to a public repository.

## Requirements

- Python 3.10 or later recommended
- No third-party packages required

## How to Run

1. Clone or download this repository.
2. Open a terminal in the project directory.
3. Run the application:

```bash
python main.py
```

4. Follow the on-screen menu to manage your expenses.

## Run the Tests

Run the test suite with:

```bash
python -m unittest -v test_expense_tracker
```

The tests use a temporary SQLite database so they can verify database operations without modifying your normal expense database.

## What I Learned

- Working with SQLite and SQL queries
- Separating database operations from application logic
- Building a menu-driven command-line application
- Validating user input and handling errors
- Writing unit tests with Python's `unittest`
- Using temporary databases for isolated testing

## Future Improvements

- Monthly and yearly spending reports
- Export expenses to CSV
- Budget limits and spending alerts
- Improved command-line interface
- More automated tests for edge cases

## License

This project is available for educational and portfolio use. Add a license file if you want to specify formal reuse and distribution permissions.
