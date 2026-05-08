"""
Application configuration.

Single configuration class for the application using a local SQLite database.
"""

import os


class Config:
    """Application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "test-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///customers.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
