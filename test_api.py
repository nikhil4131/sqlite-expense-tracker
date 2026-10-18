
import sqlite3

import pytest
from fastapi.testclient import TestClient

from api import main as api_main



@pytest.fixture
def client(tmp_path, monkeypatch):
    # Create a separate SQLite database for each test.
    test_db = tmp_path / "test_expenses.db"

    def test_initialize_database():
        connection = sqlite3.connect(test_db)
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

    # Force API requests to use SQLite during tests.
    monkeypatch.setattr(
        api_main,
        "use_postgres",
        lambda: False,
    )

    monkeypatch.setattr(
        api_main,
        "initialize_database",
        test_initialize_database,
    )

    monkeypatch.setitem(
        api_main.app.dependency_overrides,
        api_main.get_current_user,
        lambda: {"id": "test-user-123"},
    )
    return TestClient(api_main.app)



def test_get_expenses_returns_empty_list(client):
    response = client.get("/expenses")

    assert response.status_code == 200
    assert response.json() == []


def test_create_expense(client):
    response = client.post(
        "/expenses",
        json={
            "amount": 125,
            "category": "Food",
            "description": "Lunch",
            "date": "2026-10-15"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Expense created successfully"

    expenses = client.get("/expenses").json()

    assert len(expenses) == 1
    assert expenses[0]["amount"] == 125
    assert expenses[0]["category"] == "Food"


def test_create_expense_rejects_negative_amount(client):
    response = client.post(
        "/expenses",
        json={
            "amount": -50,
            "category": "Food",
            "description": "Invalid expense",
            "date": "2026-10-15"
        }
    )

    assert response.status_code == 422


def test_update_expense(client):
    created = client.post(
        "/expenses",
        json={
            "amount": 100,
            "category": "Food",
            "description": "Lunch",
            "date": "2026-10-15"
        }
    )

    expense_id = created.json()["expense"]["id"]

    response = client.put(
        f"/expenses/{expense_id}",
        json={
            "amount": 150,
            "category": "Travel",
            "description": "Taxi",
            "date": "2026-10-15"
        }
    )

    assert response.status_code == 200

    expenses = client.get("/expenses").json()

    assert len(expenses) == 1
    assert expenses[0]["amount"] == 150
    assert expenses[0]["category"] == "Travel"


def test_delete_expense(client):
    created = client.post(
        "/expenses",
        json={
            "amount": 100,
            "category": "Food",
            "description": "Lunch",
            "date": "2026-10-15"
        }
    )

    expense_id = created.json()["expense"]["id"]

    response = client.delete(f"/expenses/{expense_id}")

    assert response.status_code == 200
    assert client.get("/expenses").json() == []


def test_update_missing_expense_returns_404(client):
    response = client.put(
        "/expenses/99999",
        json={
            "amount": 100,
            "category": "Food",
            "description": "Lunch",
            "date": "2026-10-15"
        }
    )

    assert response.status_code == 404


def test_delete_missing_expense_returns_404(client):
    response = client.delete("/expenses/99999")

    assert response.status_code == 404

def test_create_expense_rejects_whitespace_category(client):
    response = client.post(
        "/expenses",
        json={
            "amount": 100,
            "category": "   ",
            "description": "Lunch",
            "date": "2026-10-15"
        }
    )

    assert response.status_code == 422


def test_create_expense_rejects_invalid_date(client):
    response = client.post(
        "/expenses",
        json={
            "amount": 100,
            "category": "Food",
            "description": "Lunch",
            "date": "2026-02-30"
        }
    )

    assert response.status_code == 422

def test_get_expenses_requires_authentication(client):
    api_main.app.dependency_overrides.pop(
        api_main.get_current_user,
        None,
    )

    response = client.get("/expenses")

    assert response.status_code == 401
