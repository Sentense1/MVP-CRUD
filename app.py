
""" importing all necessary modules """

from flask import Flask, render_template, flash, request, redirect, url_for, session
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, current_user
from model import Database, User

# Create a Flask app
app = Flask(__name__)
# Configure the secret key for encrypting session data
app.secret_key = 'secret key'


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
# Configure the login view (the view function that handles logins)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    """handles flask_login loading"""

    # Create a new Database instance to connect to the MySQL database.
    db = Database()
    # Get a cursor for executing SQL queries on the database.
    cursor = db.cursor

    # Execute a SQL query to select a user from the 'users' table based on their 'id'.
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

    # Fetch the first (and only) row of the result, which should contain user data.
    user_data = cursor.fetchone()

    # Close the database connection to release resources.
    db.close()

    # If user data is found in the database:
    if user_data:
        # Create a User object representing the logged-in user
        user = User(user_id=user_data['id'])
        # Return the User object representing the logged-in user.
        return user
    else:
        # If no user data is found, return None to indicate no authenticated user.
        return None


@app.route('/')
def index():
    """rendering landing page"""
    return render_template('index.html')


@app.route('/home')
@login_required
def home():
    """rendering students data to home"""

    try:
        # Create a new Database instance to connect to the MySQL database.
        db = Database()
        # Get a cursor for executing SQL queries on the database.
        cursor = db.cursor

        # Execute a SQL query to select all students' data from the 'students' table.
        cursor.execute("SELECT * FROM students;")

        # Fetch all rows of the result, which represent student records.
        students = cursor.fetchall()

        # Render the 'home.html' template and pass the 'students' data to the template.
        return render_template('home.html', students=students)

    except Exception as e:
        # Print an error message if any exception occurs.
        print("Error:", str(e))
    finally:
        if db:
            # Ensure that the database connection is closed in all cases.
            db.close()

    # Render the 'home.html' template even if there's an error.
    return render_template('home.html')


@app.route('/info')
def info():
    """rendering students data to info page"""

    try:
        # Create a new Database instance to connect to the MySQL database.
        db = Database()
        # Get a cursor for executing SQL queries on the database.
        cursor = db.cursor

        # Execute a SQL query to select all students' data from the 'students' table.
        cursor.execute("SELECT * FROM students;")

        # Fetch all rows of the result, which represent student records.
        students = cursor.fetchall()

    except Exception as e:
        # Print an error message if any exception occurs.
        print("Error:", str(e))
    finally:
        if db:
            # Ensure that the database connection is closed in all cases.
            db.close()

    # Render the 'home.html' template even if there's an error.
    return render_template('info.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """rendering login page"""
    if current_user.is_authenticated:
        # If the user is already logged in, redirect them to the home page
        return redirect(url_for('home'))
    if request.method == 'POST':
        # Check if the HTTP request method is POST (form submission)
        username = request.form['username']
        password = request.form['password']

        try:
            # Try to establish a database connection
            db = Database()
            cursor = db.cursor

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
                    db.close()
                    # Redirect the user to the 'home' page upon successful login.
                    return redirect(url_for('home'))

                else:
                    # If the password is incorrect, display an error flash message.
                    flash('Login failed. Check your password.', 'error')

            else:
                # If the username is not found, display an error flash message.
                flash('Login failed. Check your username.', 'error')
            # Close the database connection.
            db.close()

        except Exception as e:
            # Print an error message if any exception occurs.
            print("Error:", str(e))

    # Render the 'login.html' template if the request method is GET or if login fails.
    return render_template('login.html')


@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    """ Rendering the add student page """
    if 'username' in session:
        # Check if the user is logged in (the 'username' is in the session)
        if request.method == 'POST':
            # Check if the HTTP request method is POST (form submission)
            # Get form data
            name = request.form.get('name')
            phoneNumber = request.form.get('phoneNumber')
            email = request.form.get('email')

            # Create a cursor and execute the INSERT query
            db = Database()
            cursor = db.cursor
            cursor.execute("INSERT INTO students (Name, PhoneNumber, Email) VALUES (%s, %s, %s)",
                           (name, phoneNumber, email))

            # Commit the changes to the database
            db.conn.commit()
            # Close the cursor
            cursor.close()
            # Close the database connection
            db.close()

            # Flash a success message
            flash('Student added successfully!', 'success')

            # Redirect to the student information page
            return redirect(url_for('home'))

        # If the request method is GET (initial page load), render the add student form
        return render_template('add_student.html')


@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit(student_id):
    """ rendering edit page"""
    if 'username' in session:

        # Fetch the existing student data
        db = Database()
        # Create a new Database instance to connect to the MySQL database.
        cursor = db.cursor
        # Get a cursor for executing SQL queries on the database.
        cursor.execute("SELECT * FROM students WHERE ID = %s", (student_id,))
        # Fetch the first (and only) row of the result, which should contain student data.
        student = cursor.fetchone()

        # Close the database connection to release resources.
        db.close()
        # Check if the student exists
        if request.method == 'POST':
            # Check if the HTTP request method is POST (form submission)
            name = request.form.get('name')
            # Get form data
            phoneNumber = request.form.get('phoneNumber')
            email = request.form.get('email')

            # Check if 'Name' is not empty
            if not name:
                # Redirect back to the edit form
                return redirect(url_for('edit', student_id=student_id))
            # strips trailing and leading spaces from name input
            if name:
                name.strip()
            # Check if 'phoneNumber' is not empty
            if not phoneNumber:
                flash('Phone Number cannot be empty!', 'error')
                # Redirect back to the edit form
                return redirect(url_for('edit', student_id=student_id))
            # strips trailing and leading spaces from phoneNumber input
            if phoneNumber:
                phoneNumber.strip()
            # Check if 'email' is not empty
            if not email:
                flash('Email cannot be empty!', 'error')
                # Redirect back to the edit form
                return redirect(url_for('edit', student_id=student_id))
            # strips trailing and leading spaces from email input
            if email:
                email.strip()

            # Create a cursor and execute the UPDATE query
            db = Database()
            # Create a new Database instance to connect to the MySQL database.
            cursor = db.cursor
            # Get a cursor for executing SQL queries on the database.
            update_query = "UPDATE students SET Name = %s, PhoneNumber = %s, Email = %s WHERE ID = %s"
            # Execute the UPDATE query
            cursor.execute(
                update_query, (name, phoneNumber, email, student_id))
            # Commit the changes to the database
            db.conn.commit()
            # Close the cursor
            cursor.close()
            # Close the database connection3
            db.close()

            # Flash a success message
            flash('Student information updated successfully!', 'success')

            # Redirect back to the info page
            return redirect(url_for('home'))

        # If it's a GET request, fetch the student data and display the edit form
        db = Database()
        # Create a new Database instance to connect to the MySQL database.
        cursor = db.cursor
        # Get a cursor for executing SQL queries on the database.
        cursor.execute("SELECT * FROM students WHERE ID = %s", (student_id,))
        # Fetch the first (and only) row of the result, which should contain student data.
        student = cursor.fetchone()
        # Close the database connection to release resources.
        db.close()

        # Pass the student data to the edit form template
        return render_template('edit.html', student=student)


@app.route('/delete/<int:student_id>', methods=['POST'])
@login_required
def delete(student_id):
    """ delete students """
    # Check if the user is logged in (the 'username' is in the session)
    if 'username' in session:

        # Create a new Database instance to connect to the MySQL database.
        db = Database()
        # Get a cursor for executing SQL queries on the database.
        cursor = db.cursor
        # Execute a SQL query to select a student from the 'students' table based on their 'id'.
        cursor.execute("SELECT * FROM students WHERE ID = %s", (student_id,))
        # Fetch the first (and only) row of the result, which should contain student data.
        student_data = cursor.fetchone()
        # Close the database connection to release resources.
        if student_data:

            # Delete the student record from the 'students' table
            delete_query = "DELETE FROM students WHERE ID = %s"
            # Execute the DELETE query
            cursor.execute(delete_query, (student_id,))

            # Commit the changes to the database
            db.conn.commit()
            # Close the cursor
            cursor.close()
            # Close the database connection
            db.close()

            # Flash a success message
            flash('Student deleted successfully!', 'success')
        else:
            # If student data is not found, show an error message
            flash('Student not found', 'error')

        # Redirect back to the info page
        return redirect(url_for('home'))

# Route for handling the login page logic


@app.route('/about')
def about():
    """render the about page"""
    # Render the 'about.html' template
    return render_template('about.html')

# Route for handling the login page logic


@app.route('/logout')
@login_required
def logout():
    """logging out user"""
    # Check if the user is logged in (the 'username' is in the session)
    if current_user.is_authenticated:
        # Log the logout event
        logout_user()
    # Redirect to the landing page
    return redirect(url_for('info'))


# Route for handling the login page logic
if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
