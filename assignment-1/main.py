
"""
Main entry point for the Flask app.
Sets up the Flask application and registers blueprints.
"""

from flask import Flask
from app.routes.customer import customer_bp


app = Flask(__name__)
app.register_blueprint(customer_bp)

if __name__ == "__main__":
	app.run(debug=True)
