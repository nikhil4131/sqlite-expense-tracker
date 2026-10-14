import sqlite3
from datetime import datetime
from database import (
    save_expense,
    update_expense_record,
    delete_expense_record,
    calculate_total_expenses,
    initialize_database,
    get_all_expenses,
    get_category_totals,
    get_expenses_by_date_range,
    get_expense_by_id
)

def show_menu():
    print("\n===== EXPENSE TRACKER =====")
    print("1. Add expense")
    print("2. View expenses")
    print("3. Delete expense")
    print("4. Update expense")
    print("5. View spending summary")
    print("6. Filter expenses by date")
    print("7. Exit")

def add_expense(cursor, connection):
    while True:
        try:
            amount = float(input("Enter expense amount: "))

            if amount <= 0:
                print("Amount must be greater than zero.")
                continue

            break

        except ValueError:
            print("Please enter a valid number.")

    while True:
        category = input("Enter category: ").strip()

        if category:
            break

        print("Category cannot be empty.")

    description = input("Enter description: ").strip()

    while True:
        date = input("Enter date (YYYY-MM-DD): ").strip()

        try:
            datetime.strptime(date, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD, for example 2026-10-13.")


    try:
        save_expense(cursor, connection, amount, category, description, date)
        print("Expense added successfully!")
    except sqlite3.Error as error:
        connection.rollback()
        print(f"Database error: {error}")

def view_expenses(cursor):
    expenses = get_all_expenses(cursor)

    if not expenses:
        print("No expenses found.")
        return

    print("\n===== ALL EXPENSES =====")

    for expense in expenses:
        print(f"ID: {expense[0]}")
        print(f"Amount: ₹{expense[1]:.2f}")
        print(f"Category: {expense[2]}")
        print(f"Description: {expense[3]}")
        print(f"Date: {expense[4]}")
        print("-" * 25)

def delete_expense(cursor, connection):
    view_expenses(cursor)

    expense_id = input("Enter the ID of the expense to delete: ").strip()

    if not expense_id.isdigit():
        print("Please enter a valid expense ID.")
        return

    expense = get_expense_by_id(cursor, int(expense_id))

    if expense is None:
        print("No expense found with that ID.")
        return

    confirm = input("Are you sure you want to delete it? (yes/no): ").strip().lower()

    if confirm == "yes":
        delete_expense_record(cursor, connection, expense_id)
        print("Expense deleted successfully!")
    else:
        print("Deletion cancelled.")

def update_expense(cursor, connection):
    view_expenses(cursor)

    expense_id = input("Enter the ID of the expense to update: ").strip()

    if not expense_id.isdigit():
        print("Please enter a valid expense ID.")
        return

    expense = get_expense_by_id(cursor, int(expense_id))

    if expense is None:
        print("No expense found with that ID.")
        return

    print("Press Enter to keep the current value.")

    amount_input = input(f"Amount [{expense[1]}]: ").strip()
    category_input = input(f"Category [{expense[2]}]: ").strip()
    description_input = input(f"Description [{expense[3] or ''}]: ").strip()
    date_input = input(f"Date [{expense[4]}]: ").strip()

    amount = expense[1]
    category = expense[2]
    description = expense[3]
    date = expense[4]

    if amount_input:
        try:
            amount = float(amount_input)
            if amount <= 0:
                print("Amount must be greater than zero.")
                return
        except ValueError:
            print("Invalid amount.")
            return

    if category_input:
        category = category_input

    if description_input:
        description = description_input

    if date_input:
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            date = date_input
        except ValueError:
            print("Invalid date. Use YYYY-MM-DD.")
            return

    update_expense_record(
        cursor,
        connection,
        int(expense_id),
        amount,
        category,
        description,
        date
    )
    print("Expense updated successfully!")

def show_summary(cursor):
    total = calculate_total_expenses(cursor)

    print(f"\nTotal expenses: ₹{total:.2f}")

    summaries = get_category_totals(cursor)

    print("\n===== CATEGORY-WISE SPENDING =====")

    if not summaries:
        print("No expenses found.")
        return

    for category, amount in summaries:
        print(f"{category}: ₹{amount:.2f}")

def filter_expenses_by_date(cursor):
    from datetime import datetime

    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date. Use YYYY-MM-DD.")
        return

    if start > end:
        print("Start date cannot be after end date.")
        return

    expenses = get_expenses_by_date_range(
        cursor, start_date, end_date
    )

    if not expenses:
        print("No expenses found in this date range.")
        return

    print(f"\n===== EXPENSES FROM {start_date} TO {end_date} =====")

    total = 0

    for expense in expenses:
        print(f"ID: {expense[0]}")
        print(f"Amount: ₹{expense[1]:.2f}")
        print(f"Category: {expense[2]}")
        print(f"Description: {expense[3]}")
        print(f"Date: {expense[4]}")
        print("-" * 25)
        total += expense[1]

    print(f"Total for this period: ₹{total:.2f}")

def main():
    connection, cursor = initialize_database()

    connection.commit()

    while True:
        show_menu()

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            add_expense(cursor, connection)

        elif choice == "2":
            view_expenses(cursor)

        elif choice == "3":
            delete_expense(cursor, connection)

        elif choice == "4":
            update_expense(cursor, connection)

        elif choice == "5":
            show_summary(cursor)

        elif choice == "6":
            filter_expenses_by_date(cursor)

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    connection.close()
    pass

if __name__ == "__main__":
    main()
