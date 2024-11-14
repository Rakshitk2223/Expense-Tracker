from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required
import mysql.connector
from config import DB_CONFIG
from user import User

# Define the blueprint
auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")  # Set URL prefix to '/auth' for all routes in this blueprint
bcrypt = Bcrypt()  # Initialize Bcrypt without attaching to an app instance

# User registration route within the auth blueprint
@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            db.commit()
        except mysql.connector.Error as err:
            db.rollback()
            flash("Registration failed. Please try again.")
            return render_template('register.html')
        finally:
            cursor.close()
            db.close()

        flash("Registration successful. Please log in.")
        return redirect(url_for('auth.login'))  # Redirect to the auth blueprint's login page

    return render_template('register.html')

# User login route within the auth blueprint
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user_data = cursor.fetchone()
        
        cursor.close()
        db.close()

        if user_data:
            print("User found:", user_data)  # Debug output for user data
            # Check if password matches
            if bcrypt.check_password_hash(user_data['password'], password):
                user = User(user_data['id'], user_data['username'], user_data['email'])
                login_user(user)
                print("Login successful")  # Debug output for successful login
                return redirect(url_for('dashboard'))

            else:
                print("Password does not match")  # Debug output for password mismatch
        else:
            print("No user found with this email")  # Debug output for email mismatch

        flash('Login failed. Check your email and password.')
    
    return render_template('login.html')


# User logout route within the auth blueprint
@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('auth.login'))
