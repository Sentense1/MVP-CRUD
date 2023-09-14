""" importing all necessary modules """

# Import the 'os' module, for reading the environment variable.
import os
# Import the 'Flask' class from the 'flask' module, for creating the Flask application.
from flask import Flask, render_template, flash, request, redirect, url_for, make_response
# Import the 'LoginManager' class from the 'flask_login' module, for managing user logins.
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
# Import the 'load_dotenv' func for loading environment variables from a '.env' file.
from dotenv import load_dotenv
# Import the 'Error' class, for handling MySQL errors.
from mysql.connector import Error
# Import the 'Database' and 'user' class.
from model import Database, User
# Import the 'errors' Blueprint
from handlers import errors


# Load environment variables from the '.env' file
load_dotenv()

# Create a Flask app
app = Flask(__name__)

# Configure the secret key for encrypting session data
app.secret_key = os.getenv('SECRET_KEY')


# Initialize Flask-Login
login_manager = LoginManager()
# Configure the application to use Flask-Login
login_manager.init_app(app)
# Configure the login view to be the 'login' route
login_manager.login_view = 'login'

# Register the 'errors' Blueprint
app.register_blueprint(errors)

# Configure the remember cookie name
app.config['REMEMBER_COOKIE_NAME'] = 'remember_token'


# Define a function to load a user from their user_id
@login_manager.user_loader
def load_user(user_id):
    """Handles flask_login loading."""

    # Create a new Database instance to connect to the MySQL database.
    data_base = Database()
    # Get a cursor for executing SQL queries on the database.
    cursor = data_base.cursor

    # Execute a query to select a user from the 'users' table.
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

    # Fetch the first (and only) row of the result.
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
        # If no user data is found, return None.
        return None


# Define the 'index' route
@app.route('/')
def index():
    """Rendering landing page."""
    # Render the 'index.html' template.
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

        # Execute a query to select all students' data.
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

    # Render the 'home.html' template.
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

        # Execute a SQL query to select all students' data
        cursor.execute("SELECT * FROM students;")

        # Fetch all rows of the result
        students = cursor.fetchall()

    except Error as mysql_error:
        # Handle MySQL-related exceptions
        print("MySQL Error:", str(mysql_error))
    finally:
        if data_base:
            # Ensure that the database connection is closed in all cases.
            data_base.close()

    # Render the 'students information.html' template.
    return render_template('info.html', students=students)


# Define the 'login' route
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rendering login page."""
    # If the user is already logged in
    if current_user.is_authenticated:
        # Redirect them to the home page
        return redirect(url_for('home'))
    # Check if the HTTP request method is POST
    if request.method == 'POST':
        # Get the username and password from the form
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
                    login_user(user_obj, remember=False)

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
    # Check if the user is logged in
    if current_user.is_authenticated:
        # Check if the HTTP request method is POST
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

        # If the request method is GET, render the add student form
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
            # Get id query
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

        # Create a new Database instance to connect to the MySQL database.
        data_base = Database()
        # Get a cursor for executing SQL queries on the database.
        cursor = data_base.cursor
        # Execute a SQL query to select a student from the 'students' table.
        cursor.execute("SELECT * FROM students WHERE ID = %s", (student_id,))
        # Fetch the first (and only) row of the result.
        student = cursor.fetchone()
        # Close the database connection to release resources.
        data_base.close()

        # Pass the student data to the edit form template
        return render_template('edit.html', student=student)


@app.route('/delete/<int:student_id>', methods=['POST'])
@login_required
def delete(student_id):
    """ Deletes students. """
    # Check if the user is logged in
    if current_user.is_authenticated:

        # Create a new Database instance to connect to the MySQL database.
        data_base = Database()
        # Get a cursor for executing SQL queries on the database.
        cursor = data_base.cursor
        # Execute a SQL query to select a student from the 'students' table.
        cursor.execute("SELECT * FROM students WHERE ID = %s", (student_id,))
        # Fetch the first (and only) row of the result.
        student_data = cursor.fetchone()
        # If student data is found
        if student_data:

            # Insert the student data about to be deleted into 'archived_students' table

            # Create the INSERT query
            insert_query = "INSERT INTO archived_students (name, phoneNumber, email)"
            # Create the VALUES query
            values_query = "VALUES (%s, %s, %s)"
            # Define the data to be inserted
            student_info = (
                student_data['Name'], student_data['phoneNumber'], student_data['Email'])
            # Complete the insertion execution to 'archived_students'
            cursor.execute(insert_query + values_query, student_info)

            # Delete the student record from the 'students' table
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
        # Send a logout success message
        response = make_response("You are logged out")
        # Delete the remember cookie
        response.delete_cookie("remember_token")
    return redirect(url_for('login'))


if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
