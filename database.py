import sqlite3


def save_expense(cursor, connection, amount, category, description, date):
    cursor.execute("""
                   INSERT INTO expenses (amount, category, description, date)
                   VALUES (?, ?, ?, ?)
                   """, (amount, category, description, date))

    connection.commit()


def update_expense_record(
        cursor, connection, expense_id, amount, category, description, date
):
    cursor.execute("""
                   UPDATE expenses
                   SET amount = ?, category = ?, description = ?, date = ?
                   WHERE id = ?
                   """, (amount, category, description, date, expense_id))

    connection.commit()


def delete_expense_record(cursor, connection, expense_id):
    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )
    connection.commit()


def calculate_total_expenses(cursor):
    cursor.execute("SELECT SUM(amount) FROM expenses")
    result = cursor.fetchone()
    return result[0] or 0

def initialize_database():
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS expenses (
                                                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                           amount REAL NOT NULL,
                                                           category TEXT NOT NULL,
                                                           description TEXT,
                                                           date TEXT NOT NULL
                   )
                   """)

    connection.commit()
    return connection, cursor

def get_all_expenses(cursor):
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    return cursor.fetchall()

def get_category_totals(cursor):
    cursor.execute("""
                   SELECT category, SUM(amount)
                   FROM expenses
                   GROUP BY category
                   ORDER BY SUM(amount) DESC
                   """)

    return cursor.fetchall()

def get_expenses_by_date_range(cursor, start_date, end_date):
    cursor.execute("""
                   SELECT * FROM expenses
                   WHERE date >= ? AND date <= ?
                   ORDER BY date
                   """, (start_date, end_date))

    return cursor.fetchall()

def get_expense_by_id(cursor, expense_id):
    cursor.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (expense_id,)
    )
    return cursor.fetchone()

def get_expense_by_id(cursor, expense_id):
    cursor.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (expense_id,)
    )
    return cursor.fetchone()
