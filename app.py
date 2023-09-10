""" Importing necessary modules """

from flask import Flask, render_template, request, url_for


# creating my app
app = Flask(__name__)


# creating landing page route
@app.route('/')
def index():
    """ landing page route """
    return render_template('index.html')


# creating home page route
@app.route('/home')
def home():
    """ route for displaying student information """
    return render_template('home.html')


# creating login page route
@app.route('/login')
def login():
    """ route for logging in """
    return render_template('index.html')


# creating edit page route
@app.route('/edit')
def edit():
    """ route for editing student information """
    return render_template('edit.html')


# creating add student page route
@app.route('add_student')
def add_student():
    """ route for adding students information"""
    return render_template('add_student.html')


# creating logout page route
@app.route('/logout')
def logout():
    """ route for loggin out """
    return redirect(url_for('index'))


if __name__ == '__maim__':
    app.run(debug=True)
