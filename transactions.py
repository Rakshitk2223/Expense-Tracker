from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import mysql.connector
from config import DB_CONFIG

# Define the transactions blueprint
transactions_blueprint = Blueprint("transactions", __name__)

# Route for adding a transaction
@transactions_blueprint.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    try:
        data = {
            'amount': request.form['amount'],
            'category': request.form['category'],
            'description': request.form['description'],
            'date': request.form['date'],
            'type': request.form['type']
        }

        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO transactions (user_id, amount, category_id, description, date, type) VALUES (%s, %s, %s, %s, %s, %s)",
            (current_user.id, data['amount'], data['category'], data['description'], data['date'], data['type'])
        )
        db.commit()
        flash("Transaction added successfully!", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('dashboard'))

# Route for deleting a transaction
@transactions_blueprint.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        # Ensure the transaction belongs to the current user
        cursor.execute(
            "DELETE FROM transactions WHERE id = %s AND user_id = %s",
            (transaction_id, current_user.id)
        )
        db.commit()
        
        if cursor.rowcount == 0:
            # If no rows were affected, the transaction wasn't found or didn't belong to the user
            return {"success": False, "message": "Transaction not found or access denied"}, 404

        return {"success": True, "message": "Transaction deleted successfully"}, 200

    except Exception as e:
        return {"success": False, "message": f"An error occurred: {e}"}, 500

    finally:
        cursor.close()
        db.close()
