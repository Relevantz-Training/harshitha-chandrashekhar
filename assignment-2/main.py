"""
Application factory and entry point.

Creates and configures the Flask application, initialises the database,
seeds default data, and registers all blueprints.

Usage
-----
Run directly::

    python main.py
"""

from flask import Flask

from config import Config
from database import init_db, db
from routes.customer import customer_bp


def create_app() -> Flask:
    """
    Application factory.

    Creates a Flask application instance, binds configuration, initialises
    the database (creating tables if they do not exist), seeds sample data,
    and registers the customer blueprint.

    Returns:
        Flask: A fully configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialise database (creates tables via SQLAlchemy)
    init_db(app)

    # Seed sample data so the API works immediately out of the box
    _seed_development_data(app)

    # Register blueprints
    app.register_blueprint(customer_bp)

    return app


def _seed_development_data(app: Flask):
    """
    Insert a handful of sample customer rows if the table is empty.

    Args:
        app (Flask): The Flask application instance (provides app context).
    """
    from models.customer import Customer

    with app.app_context():
        if Customer.query.count() == 0:
            sample_customers = [
                Customer(name="Alice Smith",  email="alice@example.com",   phone="123-456-7890"),
                Customer(name="Bob Johnson",  email="bob@example.com",     phone="234-567-8901"),
                Customer(name="Charlie Lee",  email="charlie@example.com", phone="345-678-9012"),
            ]
            db.session.bulk_save_objects(sample_customers)
            db.session.commit()
            print("✅  Development seed data inserted.")


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True)
