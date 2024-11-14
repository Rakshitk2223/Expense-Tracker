from flask_login import UserMixin
import mysql.connector
from config import DB_CONFIG
from extensions import login_manager  # Adjust path if app is in a different module


class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

    @staticmethod
    def get_by_email(email):
        """Retrieve a user by email."""
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        db.close()

        if user_data:
            return User(user_data['id'], user_data['username'], user_data['email'])
        return None

    @staticmethod
    def get(user_id):
        """Retrieve a user by ID."""
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        db.close()

        if user_data:
            return User(user_data['id'], user_data['username'], user_data['email'])
        return None

@login_manager.user_loader  # type: ignore
def load_user(user_id):
    return User.get(user_id)