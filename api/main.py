from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import (initialize_database,
                      get_all_expenses,
                      save_expense,
                      update_expense_record,
                      delete_expense_record,)
from pydantic import BaseModel, Field, field_validator
from datetime import date as Date

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0, allow_inf_nan=False)
    category: str = Field(min_length=1, max_length=50)
    description: str = Field(default="", max_length=200)
    date: Date

    @field_validator("category")
    @classmethod
    def validate_category(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Category cannot be empty or whitespace")

        return value

    @field_validator("description")
    @classmethod
    def clean_description(cls, value):
        return value.strip()


@app.get("/health")
def check_health():
    return {"status": "healthy"}

@app.get("/expenses")
def get_expenses():
    connection, cursor = initialize_database()

    try:
        expenses = get_all_expenses(cursor)

        return [
            {
                "id": expense[0],
                "amount": expense[1],
                "category": expense[2],
                "description": expense[3],
                "date": expense[4]
            }
            for expense in expenses
        ]

    finally:
        connection.close()

@app.post("/expenses")
def create_expense(expense: ExpenseCreate):
    connection, cursor = initialize_database()

    try:
        expense_id = save_expense(
            cursor,
            connection,
            expense.amount,
            expense.category.strip(),
            expense.description.strip(),
            expense.date
        )

        return {
            "message": "Expense created successfully",
            "expense": {
                "id": expense_id,
                "amount": expense.amount,
                "category": expense.category.strip(),
                "description": expense.description.strip(),
                "date": expense.date
            }
        }

    finally:
        connection.close()

@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: ExpenseCreate):
    connection, cursor = initialize_database()

    try:
        cursor.execute(
            "SELECT id FROM expenses WHERE id = ?",
            (expense_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Expense not found"
            )

        update_expense_record(
            cursor,
            connection,
            expense_id,
            expense.amount,
            expense.category.strip(),
            expense.description.strip(),
            expense.date
        )

        return {
            "message": "Expense updated successfully",
            "id": expense_id
        }

    finally:
        connection.close()

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    connection, cursor = initialize_database()

    try:
        cursor.execute(
            "SELECT id FROM expenses WHERE id = ?",
            (expense_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Expense not found"
            )

        delete_expense_record(cursor, connection, expense_id)

        return {
            "message": "Expense deleted successfully",
            "id": expense_id
        }

    finally:
        connection.close()
