""" necessary modules"""
# import logging
from flask_login import UserMixin
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash
from decouple import config

# Configure logging
# logging.basicConfig(filename='app.log', level=logging.ERROR,
#                    format='%(asctime)s - %(levelname)s - %(message)s')


# Define the User class
class User(UserMixin):
    """User database class"""

    def __init__(self, user_id):
        # Initialize the User object with a user_id (loaded from the database)
        self.id = user_id

    @staticmethod
    def verify_password(saved_password_hash, provided_password):
        """Verify password"""
        # Static method to verify a provided password against a saved hashed password
        return check_password_hash(saved_password_hash, provided_password)


# Define the Database class
class Database:
    """Database class for managing database connections"""

    def __init__(self):
        try:
            # Establish a connection to the MySQL database using environment variables
            self.conn = mysql.connector.connect(
                host=config('DB_HOST'),
                user=config('DB_USER'),
                password=config('DB_PASSWORD'),
                database=config('DB_NAME')
            )

            # Check if the connection is successful
            if self.conn.is_connected():
                # Create a cursor object for executing SQL queries and return results as dictionaries
                self.cursor = self.conn.cursor(dictionary=True)
        except Error as e:
            # Print an error message if connection fails
            print("Error connecting to mySQL", e)
            # error_message = f"Error connecting to mySQL: {e}"
            # logging.error(error_message)

    def close(self):
        """Close the database connection"""

        # Check if the database connection is open
        if self.conn.is_connected():
            # Close the cursor to release resources
            self.cursor.close()
            # Close the database connection itself
            self.conn.close()
