from typing import Optional
from app.database import get_db_connection


class UserRepository:

    async def get_by_email(self, email: str) -> Optional[dict]:
        """Fetch a user record by email from MySQL."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, name, email, password_hash FROM users WHERE email = %s",
                (email,),
            )
            user = cursor.fetchone()
            return user
        finally:
            cursor.close()
            conn.close()

    async def create_user(
        self, email: str, name: str, password_hash: str
    ) -> dict:
        """Insert a new user record into MySQL."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, password_hash),
            )
            conn.commit()
            user_id = cursor.lastrowid
            return {
                "id": user_id,
                "name": name,
                "email": email,
                "password_hash": password_hash,
            }
        finally:
            cursor.close()
            conn.close()


# Singleton instance
user_repository = UserRepository()