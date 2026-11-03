import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def is_database_enabled():
    """
    Return True only when database persistence has been
    explicitly enabled.

    The troubleshooting application can operate without
    PostgreSQL when this is False.
    """

    return os.getenv(
        "DATABASE_ENABLED",
        "false"
    ).strip().lower() == "true"


def get_connection():
    """
    Create a PostgreSQL connection when database
    persistence is enabled.
    """

    if not is_database_enabled():
        raise RuntimeError(
            "Database persistence is disabled."
        )

    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )