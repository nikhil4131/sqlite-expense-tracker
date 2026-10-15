
from db_config import get_database_url
import psycopg


def main():
    database_url = get_database_url()

    if not database_url:
        print("DATABASE_URL is missing.")
        return

    try:
        with psycopg.connect(database_url, connect_timeout=10) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database(), version()")
                database_name, version = cursor.fetchone()

                print("Connection successful!")
                print(f"Database: {database_name}")
                print(f"PostgreSQL version: {version.split()[1]}")
    except Exception as error:
        print(f"Connection failed: {type(error).__name__}: {error}")


if __name__ == "__main__":
    main()
