"""
main.py – Starts the Flask app.

How to use:
1. Install packages: pip install -r requirements.txt
2. Run server: python main.py
3. Run tests: pytest
"""

import logging

from flask import Flask

from config import Config
from routes.posts import posts_bp
from routes.users import users_bp

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)


def create_app(config_object: object = Config) -> Flask:
    """
    Makes and sets up the Flask app.

    config_object: The config to use (default is Config).
    Returns: The Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Add routes for posts and users
    app.register_blueprint(posts_bp)
    app.register_blueprint(users_bp)

    return app


if __name__ == "__main__":
    # Start the app if this file is run directly
    flask_app = create_app()
    flask_app.run(
        host="0.0.0.0",
        port=5000,
        debug=flask_app.config.get("DEBUG", False),
    )
