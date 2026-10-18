from contextlib import asynccontextmanager
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    status,
    Path
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from fastapi.middleware.cors import CORSMiddleware
from database import (initialize_database,
                      get_all_expenses,
                      save_expense,
                      update_expense_record,
                      delete_expense_record,)
from pydantic import BaseModel, Field, field_validator
from datetime import date as Date

import os

from postgres_database import (
    get_postgres_connection,
    initialize_postgres_database,
    get_all_postgres_expenses,
    save_postgres_expense,
    update_postgres_expense,
    delete_postgres_expense,
    get_postgres_expense_by_id,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if use_postgres():
        connection = initialize_postgres_database()
        connection.close()

    yield


app = FastAPI(lifespan=lifespan)


security = HTTPBearer(auto_error=False)


def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "").strip()

    if not supabase_url or not publishable_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication is not configured",
        )

    try:
        response = httpx.get(
            f"{supabase_url}/auth/v1/user",
            headers={
                "apikey": publishable_key,
                "Authorization": f"Bearer {token}",
            },
            timeout=5.0,
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = response.json()

    if not user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user response",
        )

    return user

def use_postgres():
    return bool(os.getenv("DATABASE_URL", "").strip())


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "https://expense-tracker-dashboard-z9zx.onrender.com",
    ],
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
def get_expenses(user: dict = Depends(get_current_user)):
    user_id = user["id"]

    if use_postgres():
        connection = get_postgres_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, amount, category, description, date
                    FROM public.expenses
                    WHERE user_id = %s
                    ORDER BY date DESC, id DESC
                    """,
                    (user_id,)
                )
                expenses = cursor.fetchall()

            return [
                {
                    "id": expense[0],
                    "amount": expense[1],
                    "category": expense[2],
                    "description": expense[3],
                    "date": expense[4].isoformat()
                    if hasattr(expense[4], "isoformat")
                    else expense[4],
                }
                for expense in expenses
            ]
        finally:
            connection.close()

    # Keep local SQLite development working for now.
    connection, cursor = initialize_database()

    try:
        expenses = get_all_expenses(cursor)

        return [
            {
                "id": expense[0],
                "amount": expense[1],
                "category": expense[2],
                "description": expense[3],
                "date": expense[4],
            }
            for expense in expenses
        ]
    finally:
        connection.close()




@app.post("/expenses")
def create_expense(
        expense: ExpenseCreate,
        user: dict = Depends(get_current_user),
):
    if use_postgres():
        connection = get_postgres_connection()

        try:
            with connection.cursor() as cursor:
                expense_id = save_postgres_expense(
                    cursor,
                    connection,
                    expense.amount,
                    expense.category,
                    expense.description,
                    expense.date,
                    user["id"],
                )

            return {
                "message": "Expense created successfully",
                "expense": {
                    "id": expense_id,
                    "amount": expense.amount,
                    "category": expense.category,
                    "description": expense.description,
                    "date": expense.date.isoformat(),
                },
            }
        finally:
            connection.close()

    connection, cursor = initialize_database()

    try:
        expense_id = save_expense(
            cursor,
            connection,
            expense.amount,
            expense.category,
            expense.description,
            expense.date,
        )

        return {
            "message": "Expense created successfully",
            "expense": {
                "id": expense_id,
                "amount": expense.amount,
                "category": expense.category,
                "description": expense.description,
                "date": expense.date.isoformat(),
            },
        }
    finally:
        connection.close()



@app.put("/expenses/{expense_id}")
def update_expense(
        expense: ExpenseCreate,
        expense_id: int = Path(ge=1),
        user: dict = Depends(get_current_user),
                   ):
    if use_postgres():
        connection = get_postgres_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id
                    FROM public.expenses
                    WHERE id = %s AND user_id = %s
                    """,
                    (expense_id, user["id"]),
                )

                existing = cursor.fetchone()

                if existing is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Expense not found",
                    )

                update_postgres_expense(
                    cursor,
                    connection,
                    expense_id,
                    expense.amount,
                    expense.category,
                    expense.description,
                    expense.date,
                    user["id"],
                )

            return {
                "message": "Expense updated successfully",
                "id": expense_id,
            }
        finally:
            connection.close()

    connection, cursor = initialize_database()

    try:
        cursor.execute(
            "SELECT id FROM expenses WHERE id = ?",
            (expense_id,),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        update_expense_record(
            cursor,
            connection,
            expense_id,
            expense.amount,
            expense.category,
            expense.description,
            expense.date,
        )

        return {
            "message": "Expense updated successfully",
            "id": expense_id,
        }
    finally:
        connection.close()



@app.delete("/expenses/{expense_id}")
def delete_expense(
        expense_id: int = Path(ge=1),
        user: dict = Depends(get_current_user),
):
    if use_postgres():
        connection = get_postgres_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id
                    FROM public.expenses
                    WHERE id = %s AND user_id = %s
                    """,
                    (expense_id, user["id"]),
                )

                existing = cursor.fetchone()

                if existing is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Expense not found",
                    )

                delete_postgres_expense(
                    cursor, connection, expense_id, user["id"]
                )

            return {
                "message": "Expense deleted successfully",
                "id": expense_id,
            }
        finally:
            connection.close()

    connection, cursor = initialize_database()

    try:
        cursor.execute(
            "SELECT id FROM expenses WHERE id = ?",
            (expense_id,),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        delete_expense_record(cursor, connection, expense_id)

        return {
            "message": "Expense deleted successfully",
            "id": expense_id,
        }
    finally:
        connection.close()
