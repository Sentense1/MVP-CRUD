""" Import necessary modules."""

import os
from flask_login import UserMixin
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Define the User class
class User(UserMixin):
    """User class for managing user objects."""

    def __init__(self, user_id):
        """Initialize the User object."""
        # Initialize the User object with a user_id (loaded from the database)
        self.id = user_id

    @staticmethod
    def verify_password(saved_password_hash, provided_password):
        """Verify a provided password against a saved hashed password."""
        # Verify a provided password against a saved hashed password
        return check_password_hash(saved_password_hash, provided_password)


# Define the Database class
class Database:
    """Database class for managing database connections."""

    def __init__(self):
        """Initialize the Database object."""
        try:
            # Establish a connection to the MySQL database using environment variables
            self.conn = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )

            # Check if the connection is successful
            if self.conn.is_connected():
                # Create a cursor object for executing SQL queries
                self.cursor = self.conn.cursor(dictionary=True)
        except Error as error:
            # Print an error message if connection fails
            print("Error connecting to mySQL", error)

    def close(self):
        """Close the database connection."""
        # Check if the database connection is open
        if self.conn.is_connected():
            # Close the cursor to release resources
            self.cursor.close()
            # Close the database connection itself
            self.conn.close()
