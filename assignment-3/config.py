

"""
config.py – All settings for the app in one place.

Reads secrets and options from environment variables for security.
No dev/stage/prod switching—just one config for everything.
"""


import os



class Config:
    """
    Holds all app settings. Reads from environment variables for security.
    If a setting is not found in the environment, uses a safe default.
    """

    # Flask settings
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable must be set.")
    DEBUG: bool = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    TESTING: bool = False

    # JSONPlaceholder API settings
    JSONPLACEHOLDER_BASE_URL: str = os.environ.get(
        "JSONPLACEHOLDER_BASE_URL", "https://jsonplaceholder.typicode.com"
    )
    JSONPLACEHOLDER_API_KEY: str = os.environ.get("JSONPLACEHOLDER_API_KEY", "")

    # HTTP request settings
    REQUEST_TIMEOUT_SECONDS: int = int(os.environ.get("REQUEST_TIMEOUT_SECONDS", 10))
    MAX_RETRY_ATTEMPTS: int = int(os.environ.get("MAX_RETRY_ATTEMPTS", 3))
    RETRY_WAIT_SECONDS: int = int(os.environ.get("RETRY_WAIT_SECONDS", 1))




class TestingConfig(Config):
    """
    Special settings for running tests.
    Makes sure no real API calls are made during tests.
    """
    TESTING = True
    DEBUG = False
    # Use a fake API URL so tests fail if they try to call the real API
    JSONPLACEHOLDER_BASE_URL = "https://test.invalid"
    # Make tests run fast: only try once, no waiting
    MAX_RETRY_ATTEMPTS = 1
    RETRY_WAIT_SECONDS = 0
