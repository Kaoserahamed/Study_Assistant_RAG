"""Apply non-destructive database schema updates for existing installations."""
from sqlalchemy import text

from app.database import engine


def column_exists(table: str, column: str) -> bool:
    query = text(
        "SELECT 1 FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table AND COLUMN_NAME = :column"
    )
    with engine.connect() as connection:
        return connection.execute(query, {"table": table, "column": column}).first() is not None


def main() -> None:
    if not column_exists("messages", "citations"):
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE messages ADD COLUMN citations JSON NULL AFTER content"))
        print("Added messages.citations")
    else:
        print("messages.citations already exists")


if __name__ == "__main__":
    main()
