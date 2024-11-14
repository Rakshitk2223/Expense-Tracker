from flask import Flask, redirect, url_for, render_template
from flask_bcrypt import Bcrypt
from flask_login import login_required, current_user
from extensions import login_manager
from auth import auth_blueprint
from transactions import transactions_blueprint
from markupsafe import Markup
import mysql.connector
import json
from config import DB_CONFIG

from user import User

app = Flask(__name__)
login_manager.init_app(app)  # Initialize login manager with the app
login_manager.login_view = 'auth.login'



@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)  # Ensure `get` is defined in your `User` model


# Moved load_user function from user.py to main.py
@login_manager.user_loader
def load_user(user_id):

    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    db.close()

    if user_data:
        return User(user_data['id'], user_data['username'], user_data['email'])
    return None

app.secret_key = "Rakshitk@2223"  # A strong, secure secret key

# Initialize extensions with the app
bcrypt = Bcrypt(app)

# Register blueprints with URL prefixes
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(transactions_blueprint, url_prefix="/transactions")

# Default route to redirect to login
@app.route("/")
def home():
    return redirect(url_for("auth.login"))

@app.route('/dashboard')
@login_required
def dashboard():
    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor(dictionary=True)

    chart_data = []  # Initialize chart_data to an empty list
    transactions = []  # Initialize transactions to an empty list

    try:
        # Fetch chart data
        cursor.execute(
            "SELECT categories.name, SUM(transactions.amount) AS total_expense "
            "FROM transactions "
            "INNER JOIN categories ON transactions.category_id = categories.id "
            "GROUP BY categories.name"
        )
        chart_data = cursor.fetchall()

        # Ensure chart_data is JSON-serializable
        chart_labels = [row['name'] for row in chart_data if row['name'] is not None]
        chart_values = [row['total_expense'] for row in chart_data if row['total_expense'] is not None]

        # Fetch transaction history
        cursor.execute(
            "SELECT amount, category_id, description, date, type FROM transactions "
            "ORDER BY date DESC LIMIT 10"
        )
        transactions = cursor.fetchall()

        return render_template(
            'dashboard.html',
            chart_labels=chart_labels,
            chart_values=chart_values,
            transactions=transactions,  # Pass transaction history to template
            user=current_user
        )

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "Error fetching data from database"

    finally:
        cursor.close()
        db.close()



if __name__ == "__main__":
    # Print all available routes to help with debugging
    for rule in app.url_map.iter_rules():
        print(f"Endpoint: {rule.endpoint}, URL: {rule}")

    app.run(debug=True)
    

from flask import jsonify
from mysql.connector import connect, Error

@app.route('/db_test')
def db_test():
    try:
        db = connect(**DB_CONFIG)  
        cursor = db.cursor()
        cursor.execute("SELECT 1")  # Simple query to test connection
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return jsonify({'status': 'connected', 'result': result})
    except Error as e:
        return jsonify({'status': 'error', 'message': str(e)})
