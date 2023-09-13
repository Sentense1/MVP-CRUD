""" importing all necessary modules """

import os
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from dotenv import load_dotenv
from mysql.connector import Error
from model import Database, User
from handlers import errors


# Load environment variables from the '.env' file
load_dotenv()

# Create a Flask app
app = Flask(__name__)

# Configure the secret key for encrypting session data
app.secret_key = os.getenv('SECRET_KEY')


# Initialize Flask-Login
login_manager = LoginManager()
# Configure the application to use Flask-Login for managing user sessions
login_manager.init_app(app)
# Configure the login view (the view function that handles logins)
login_manager.login_view = 'login'

# Register the 'errors' Blueprint
app.register_blueprint(errors)


# Define a function to load a user from their user_id
@login_manager.user_loader
def load_user(user_id):
    """Handles flask_login loading."""

    # Create a new Database instance to connect to the MySQL database.
    data_base = Database()
    # Get a cursor for executing SQL queries on the database.
    cursor = data_base.cursor

    # Execute a SQL query to select a user from the 'users' table.
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

    # Fetch the first (and only) row of the result, which should contain user data.
    user_data = cursor.fetchone()

    # Close the database connection to release resources.
    data_base.close()

    # If user data is found in the database:
    if user_data:
        # Create a User object representing the logged-in user
        user = User(user_id=user_data['id'])
        # Return the User object representing the logged-in user.
        return user
    else:
        # If no user data is found, return None to indicate no authenticated user.
        return None


# Define the 'index' route
@app.route('/')
def index():
    """Rendering landing page."""
    return render_template('index.html')


# Define the 'home' route
@app.route('/home')
@login_required
def home():
    """Rendering students data to home."""
    try:
        # Create a new Database instance to connect to the MySQL database.
        data_base = Database()
        # Get a cursor for executing SQL queries on the database.
        cursor = data_base.cursor

        # Execute a SQL query to select all students' data from the 'students' table.
        cursor.execute("SELECT * FROM students;")

        # Fetch all rows of the result, which represent student records.
        students = cursor.fetchall()

        # Render the 'home.html' template and pass the 'students' data to the template.
        return render_template('home.html', students=students)

    except Error as mysql_error:
        # Handle MySQL-related exceptions
        print("MySQL Error:", str(mysql_error))
    finally:
        if data_base:
            # Ensure that the database connection is closed in all cases.
            data_base.close()

    # Render the 'home.html' template even if there's an error.
    return render_template('home.html')


# Define the 'student information' route
@app.route('/info')
def info():
    """Rendering students data to information page."""
    try:
        # Create a new Database instance to connect to the MySQL database.
        data_base = Database()
        # Get a cursor for executing SQL queries on the database.
        cursor = data_base.cursor

        # Execute a SQL query to select all students' data from the 'students' table.
        cursor.execute("SELECT * FROM students;")

        # Fetch all rows of the result, which represent student records.
        students = cursor.fetchall()

    except Error as mysql_error:
        # Handle MySQL-related exceptions
        print("MySQL Error:", str(mysql_error))
    finally:
        if data_base:
            # Ensure that the database connection is closed in all cases.
            data_base.close()

    # Render the 'home.html' template even if there's an error.
    return render_template('info.html', students=students)


# Define the 'login' route
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rendering login page."""
    if current_user.is_authenticated:
        # If the user is already logged in, redirect them to the home page
        return redirect(url_for('home'))
    if request.method == 'POST':
        # Check if the HTTP request method is POST (form submission)
        username = request.form['username']
        password = request.form['password']

        try:
            # Try to establish a database connection
            data_base = Database()
            cursor = data_base.cursor

            # Execute a SQL query to retrieve user data based on the provided username.
            cursor.execute(
                "SELECT * FROM users WHERE username = %s", (username,)
            )
            # Fetch the first row of the result, which represents the user data.
            user_data = cursor.fetchone()

            # Verify the provided password against the hashed password stored in the database.
            if user_data:
                if User.verify_password(user_data['password'], password):

                    # Create a User object representing the logged-in user
                    user_obj = User(user_id=user_data['id'])

                    # Log in the user using Flask-Login.
                    login_user(user_obj)

                    # Flash a success message.
                    flash('Login successful!', 'success')
                    # Close the database connection.
                    data_base.close()
                    # Redirect the user to the 'home' page upon successful login.
                    return redirect(url_for('home'))

                else:
                    # If the password is incorrect, display an error flash message.
                    flash('Login failed. Check your password.', 'error')

            else:
                # If the username is not found, display an error flash message.
                flash('Login failed. Check your username.', 'error')
            # Close the database connection.
            data_base.close()

        except Error as mysql_error:
            # Handle MySQL-related exceptions
            print("MySQL Error:", str(mysql_error))

    # Render the 'login.html' template if the request method is GET or if login fails.
    return render_template('login.html')


# Define the 'add students Information' route
@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    """ Rendering the add student page. """
    # Check if the user is logged in (the 'username' is in the session)
    if current_user.is_authenticated:
        # Check if the HTTP request method is POST (form submission)
        if request.method == 'POST':

            # Get form data
            name = request.form.get('name')
            phone_number = request.form.get('phoneNumber')
            email = request.form.get('email')

            # Strip leading and trailing whitespace from form data
            if name:
                name.strip()
            if phone_number:
                phone_number.strip()
            if email:
                email.strip()

            # Check if the name field is empty
            if not name:
                # Redirect back to the edit form
                return redirect(url_for('add_student'))

            # Check if the phoneNumber field is empty
            if not phone_number:
                flash('Phone Number cannot be empty!', 'error')
                # Redirect back to the edit form
                return redirect(url_for('add_student'))

            # Check if the email field is empty
            if not email:
                flash('Email cannot be empty!', 'error')
                # Redirect back to the edit form
                return redirect(url_for('add_student'))

            # Create a new Database instance to connect to the MySQL database.
            data_base = Database()
            # Create a cursor
            cursor = data_base.cursor
            # Create the INSERT query
            insert_query = "INSERT INTO students (Name, PhoneNumber, Email)"
            # Create the VALUES query
            values_query = "VALUES (%s, %s, %s)"
            # Execute the INSERT query
            cursor.execute(insert_query + values_query,
                           (name, phone_number, email))

            # Commit the changes to the database
            data_base.conn.commit()
            # Close the cursor
            cursor.close()
            # Close the database connection
            data_base.close()

            # Flash a success message
            flash('Student added successfully!', 'success')

            # Redirect to the student information page
            return redirect(url_for('home'))

        # If the request method is GET (initial page load), render the add student form
        return render_template('add_student.html')


# Define the 'edit student' route
@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit(student_id):
    """ Rendering edit page."""
    # Check if the user is logged in (the 'username' is in the session)
    if current_user.is_authenticated:
        # Check if the HTTP request method is POST (form submission)
        if request.method == 'POST':
            # Get form data for name
            name = request.form.get('name')
            # Get form data for phoneNumber
            phone_number = request.form.get('phoneNumber')
            # Get form data for email
            email = request.form.get('email')

            # Strip leading and trailing whitespace from form data
            if name:
                name.strip()
            if phone_number:
                phone_number.strip()
            if email:
                email.strip()

            # Check if the name field is empty
            if not name:
                # Redirect back to the edit form
                return redirect(url_for('edit', student_id=student_id))

            # Check if the phoneNumber field is empty
            if not phone_number:
                flash('Phone Number cannot be empty!', 'error')
                # Redirect back to the edit form
                return redirect(url_for('edit', student_id=student_id))

            # Check if the email field is empty
            if not email:
                flash('Email cannot be empty!', 'error')
                # Redirect back to the edit form
                return redirect(url_for('edit', student_id=student_id))

            # Create a new Database instance to connect to the MySQL.
            data_base = Database()
            # Get a cursor for executing SQL queries on the database.
            cursor = data_base.cursor
            # Get update query
            update_query = "UPDATE students SET Name = %s, PhoneNumber = %s, Email = %s "
            id_query = "WHERE ID = %s"

            # define the data to be inserted
            form_data = (name, phone_number, email, student_id)
            # Execute the UPDATE query
            cursor.execute(
                update_query + id_query, form_data)
            # Commit the changes to the database
            data_base.conn.commit()
            # Close the cursor
            cursor.close()
            # Close the database connection3
            data_base.close()

            # Flash a success message
            flash('Student information updated successfully!', 'success')

            # Redirect back to the info page
            return redirect(url_for('home'))

        # If it's a GET request, fetch the student data and display the edit form
        data_base = Database()
        # Create a new Database instance to connect to the MySQL database.
        cursor = data_base.cursor
        # Get a cursor for executing SQL queries on the database.
        cursor.execute("SELECT * FROM students WHERE ID = %s", (student_id,))
        # Fetch the first (and only) row of the result, which should contain student data.
        student = cursor.fetchone()
        # Close the database connection to release resources.
        data_base.close()

        # Pass the student data to the edit form template
        return render_template('edit.html', student=student)


@app.route('/delete/<int:student_id>', methods=['POST'])
@login_required
def delete(student_id):
    """ Deletes students. """
    # Check if the user is logged in (the 'username' is in the session)
    if current_user.is_authenticated:

        # Create a new Database instance to connect to the MySQL database.
        data_base = Database()
        # Get a cursor for executing SQL queries on the database.
        cursor = data_base.cursor
        # Execute a SQL query to select a student from the 'students' table based on their 'id'.
        cursor.execute("SELECT * FROM students WHERE ID = %s", (student_id,))
        # Fetch the first (and only) row of the result, which should contain student data.
        student_data = cursor.fetchone()
        # If student data is found
        if student_data:

            # Insert the student data about to be deleted into 'archived_students' table
            insert_query = "INSERT INTO archived_students (name, phoneNumber, email)"
            values_query = "VALUES (%s, %s, %s)"
            student_info = (
                student_data['Name'], student_data['phoneNumber'], student_data['Email'])
            # Complete the insertion execution to 'archived_students'
            cursor.execute(insert_query + values_query, student_info)

            # Now, Delete the student record from the 'students' table
            delete_query = "DELETE FROM students WHERE ID = %s"
            # Execute the DELETE query
            cursor.execute(delete_query, (student_id,))

            # Commit the changes to the database
            data_base.conn.commit()
            # Close the cursor
            cursor.close()
            # Close the database connection
            data_base.close()

            # Flash a success message
            flash('Student deleted successfully!', 'success')
        else:
            # If student data is not found, show an error message
            flash('Student not found', 'error')

        # Redirect back to the info page
        return redirect(url_for('home'))


# Define the 'archived students' route
@app.route('/archived_students')
def archived_students():
    """ Rendering archived students page. """
    # Create a new Database instance to connect to the MySQL database.
    data_base = Database()
    # Get a cursor for executing SQL queries on the database.
    cursor = data_base.cursor
    # Execute a SQL query to select all students' data
    cursor.execute("SELECT * FROM archived_students")
    # Fetch all rows of the result, which represent student records.
    archived_student = cursor.fetchall()

    # Pass the fetched archived_students data to the template
    return render_template('archived_students.html', archived_students=archived_student)


# Define the 'about' route
@app.route('/about')
def about():
    """Render the about page."""
    # Render the 'about.html' template
    return render_template('about.html')


# Define the 'logout' route
@app.route('/logout')
@login_required
def logout():
    """Logging out user."""
    # Check if the user is logged in
    if current_user.is_authenticated:
        # Log the logout event
        logout_user()
    # Redirect to the landing page
    return redirect(url_for('info'))


if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
