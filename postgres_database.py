import psycopg
from db_config import get_database_url


def get_postgres_connection():
    database_url = get_database_url()

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not configured"
        )

    return psycopg.connect(database_url)



def initialize_postgres_database():
    connection = get_postgres_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS expenses (
                                                                   id BIGSERIAL PRIMARY KEY,
                                                                   amount DOUBLE PRECISION NOT NULL
                                                                   CHECK (amount > 0),
                               category VARCHAR(50) NOT NULL,
                               description VARCHAR(200),
                               date DATE NOT NULL
                               )
                           """)

        connection.commit()
        return connection

    except Exception:
        connection.rollback()
        connection.close()
        raise


def get_all_postgres_expenses(cursor):
    cursor.execute(
        "SELECT id, amount, category, description, date "
        "FROM expenses ORDER BY date DESC, id DESC"
    )
    return cursor.fetchall()


def save_postgres_expense(
        cursor, connection, amount, category, description, date
):
    cursor.execute(
        """
        INSERT INTO expenses (amount, category, description, date)
        VALUES (%s, %s, %s, %s)
            RETURNING id
        """,
        (amount, category, description, date)
    )
    expense_id = cursor.fetchone()[0]
    connection.commit()
    return expense_id


def update_postgres_expense(
        cursor, connection, expense_id,
        amount, category, description, date
):
    cursor.execute(
        """
        UPDATE expenses
        SET amount = %s, category = %s,
            description = %s, date = %s
        WHERE id = %s
        """,
        (amount, category, description, date, expense_id)
    )
    connection.commit()


def delete_postgres_expense(cursor, connection, expense_id):
    cursor.execute(
        "DELETE FROM expenses WHERE id = %s",
        (expense_id,)
    )
    connection.commit()


def get_postgres_expense_by_id(cursor, expense_id):
    cursor.execute(
        "SELECT id FROM expenses WHERE id = %s",
        (expense_id,)
    )
    return cursor.fetchone()
