"""Apply analytics SQL to the configured database.

Usage:
    python -m src.scripts.apply_analytics_sql

This script reads src/sql/analytics.sql and executes it against the DATABASE_URL
configured in src/config.py. It uses psycopg2 if available.
"""
import sys
from pathlib import Path
from ..config import settings

SQL_PATH = Path(__file__).resolve().parents[1] / "sql" / "analytics.sql"


def main():
    if not settings.DATABASE_URL:
        print("DATABASE_URL is not configured. Set it in .env or environment.")
        sys.exit(1)

    if not SQL_PATH.exists():
        print(f"SQL file not found: {SQL_PATH}")
        sys.exit(1)

    sql = SQL_PATH.read_text()

    try:
        import psycopg2
        from psycopg2 import sql as pgsql
    except Exception as e:
        print("psycopg2 is required to run this script. Install it from requirements.txt")
        raise

    conn = None
    try:
        # Use psycopg2 connection and autocommit so we can create functions/triggers
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql)
        cur.close()
        print("Applied analytics SQL successfully.")
    except Exception as e:
        print(f"Failed to apply analytics SQL: {e}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
