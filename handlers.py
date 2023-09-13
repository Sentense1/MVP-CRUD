""" Module for handling errors. """

from flask import Blueprint, render_template

# Create a Blueprint object for handling errors
errors = Blueprint('error', __name__)


# Define error 404 handler
@errors.app_errorhandler(404)
def error_404(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404


# Define error 403 handler
@errors.app_errorhandler(403)
def error_403(error):
    """ Handle 403 errors. """
    return render_template('403.html'), 403


# Define error 500 handler
@errors.app_errorhandler(500)
def error_500(error):
    """ Handle 500 errors. """
    return render_template('500.html'), 500
