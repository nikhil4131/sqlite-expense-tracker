import unittest
import sqlite3
import tempfile
import os
from database import (save_expense,
                  update_expense_record,
                  delete_expense_record,
                  calculate_total_expenses,
                  get_expense_by_id,
                  get_all_expenses,
                  get_category_totals,
                  get_expenses_by_date_range
                  )

class TestExpenseTracker(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.temp_file.name
        self.temp_file.close()

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
                            CREATE TABLE expenses (
                                                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                      amount REAL NOT NULL,
                                                      category TEXT NOT NULL,
                                                      description TEXT,
                                                      date TEXT NOT NULL
                            )
                            """)

    def tearDown(self):
        self.connection.close()
        os.unlink(self.db_path)

    def test_add_expense_to_database(self):
        save_expense(
            self.cursor,
            self.connection,
            150,
            "Travel",
            "Bus ticket",
            "2026-10-13"
        )

        self.cursor.execute("SELECT * FROM expenses")
        expense = self.cursor.fetchone()

        self.assertIsNotNone(expense)
        self.assertEqual(expense[1], 150)
        self.assertEqual(expense[2], "Travel")
        self.assertEqual(expense[3], "Bus ticket")
        self.assertEqual(expense[4], "2026-10-13")

    def test_update_expense(self):
        save_expense(
            self.cursor,
            self.connection,
            150,
            "Travel",
            "Bus ticket",
            "2026-10-13"
        )

        update_expense_record(
            self.cursor,
            self.connection,
            1,
            200,
            "Food",
            "Lunch",
            "2026-10-13"
        )

        self.cursor.execute(
            "SELECT amount, category, description, date "
            "FROM expenses WHERE id = ?",
            (1,)
        )
        expense = self.cursor.fetchone()

        self.assertEqual(
            expense,
            (200, "Food", "Lunch", "2026-10-13")
        )

    def test_delete_expense(self):
        save_expense(
            self.cursor,
            self.connection,
            150,
            "Travel",
            "Bus ticket",
            "2026-10-13"
        )

        delete_expense_record(
            self.cursor,
            self.connection,
            1
        )

        self.cursor.execute("SELECT * FROM expenses")
        expenses = self.cursor.fetchall()

        self.assertEqual(len(expenses), 0)

    def test_calculate_total_expenses(self):
        save_expense(
            self.cursor,
            self.connection,
            150,
            "Travel",
            "Bus ticket",
            "2026-10-13"
        )

        save_expense(
            self.cursor,
            self.connection,
            200,
            "Food",
            "Lunch",
            "2026-10-13"
        )

        save_expense(
            self.cursor,
            self.connection,
            100,
            "Food",
            "Breakfast",
            "2026-10-13"
        )

        total = calculate_total_expenses(self.cursor)

        self.assertEqual(total, 450)

    def test_total_when_no_expenses(self):
        total = calculate_total_expenses(self.cursor)

        self.assertEqual(total, 0)

    def test_get_expense_by_id(self):
        save_expense(
            self.cursor,
            self.connection,
            250,
            "Food",
            "Lunch",
            "2026-10-14"
        )

        expense = get_expense_by_id(self.cursor, 1)

        self.assertIsNotNone(expense)
        self.assertEqual(expense[1], 250)
        self.assertEqual(expense[2], "Food")

    def test_get_all_expenses(self):
        save_expense(
            self.cursor,
            self.connection,
            250,
            "Food",
            "Lunch",
            "2026-10-14"
        )

        save_expense(
            self.cursor,
            self.connection,
            100,
            "Travel",
            "Bus fare",
            "2026-10-13"
        )

        expenses = get_all_expenses(self.cursor)

        self.assertEqual(len(expenses), 2)
        self.assertEqual(expenses[0][2], "Food")
        self.assertEqual(expenses[1][2], "Travel")

    def test_get_category_totals(self):
        save_expense(
            self.cursor,
            self.connection,
            250,
            "Food",
            "Lunch",
            "2026-10-14"
        )

        save_expense(
            self.cursor,
            self.connection,
            150,
            "Food",
            "Dinner",
            "2026-10-14"
        )

        save_expense(
            self.cursor,
            self.connection,
            100,
            "Travel",
            "Bus fare",
            "2026-10-13"
        )

        summaries = get_category_totals(self.cursor)

        self.assertEqual(len(summaries), 2)
        self.assertEqual(summaries[0][0], "Food")
        self.assertEqual(summaries[0][1], 400)
        self.assertEqual(summaries[1][0], "Travel")
        self.assertEqual(summaries[1][1], 100)

    def test_get_expenses_by_date_range(self):
        save_expense(
            self.cursor,
            self.connection,
            250,
            "Food",
            "Lunch",
            "2026-10-14"
        )

        save_expense(
            self.cursor,
            self.connection,
            100,
            "Travel",
            "Bus fare",
            "2026-10-13"
        )

        save_expense(
            self.cursor,
            self.connection,
            500,
            "Shopping",
            "Shoes",
            "2026-10-10"
        )

        expenses = get_expenses_by_date_range(
            self.cursor,
            "2026-10-13",
            "2026-10-14"
        )

        self.assertEqual(len(expenses), 2)
        self.assertEqual(expenses[0][2], "Travel")
        self.assertEqual(expenses[1][2], "Food")

if __name__ == "__main__":
    unittest.main()
