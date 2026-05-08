"""
Database initialisation module.

Creates a single SQLAlchemy instance that is imported and shared across
the entire application.  The actual database binding is done inside the
application factory (main.py) using ``db.init_app(app)``.
"""

from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """
    Initialise the database extension with the Flask app and create all tables.
    Args:
        app (Flask): The Flask application instance.
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()
