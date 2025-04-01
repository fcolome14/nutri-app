import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import subprocess
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / '.env')

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def create_database():
    try:
        conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()

        if not exists:
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
        else:
            print(f"Database '{DB_NAME}' already exists, skipping creation.")

        cursor.close()
        conn.close()

    except Exception as e:
        print("❌ Error during database creation:", e)


def run_migrations():
    print("🚀 Running Django migrations...")
    try:
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("✅ Migrations completed.")
    except subprocess.CalledProcessError as e:
        print("❌ Migration failed:", e)


if __name__ == "__main__":
    create_database()
    run_migrations()
