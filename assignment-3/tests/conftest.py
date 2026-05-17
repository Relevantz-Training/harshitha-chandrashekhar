"""
Shared pytest fixtures for assignment-3.

All tests use fake data and fake HTTP calls, so nothing real happens.
If a test tries to make a real HTTP call, it will fail fast.
"""

import pytest

from main import create_app
from config import TestingConfig

# ---------------------------------------------------------------------------
# Shared sample data fixtures
# ---------------------------------------------------------------------------

SAMPLE_POST = {
    "id": 1,
    "userId": 1,
    "title": "sunt aut facere repellat provident occaecati",
    "body": "quia et suscipit\nsuscipit recusandae",
}

SAMPLE_USER = {
    "id": 1,
    "name": "Leanne Graham",
    "username": "Bret",
    "email": "Sincere@april.biz",
    "phone": "1-770-736-8031 x56442",
    "website": "hildegard.org",
    "address": {
        "street": "Kulas Light",
        "suite": "Apt. 556",
        "city": "Gwenborough",
        "zipcode": "92998-3874",
    },
    "company": {"name": "Romaguera-Crona"},
}

SAMPLE_TODOS = [
    {"id": 1, "userId": 1, "title": "delectus aut autem", "completed": False},
    {"id": 2, "userId": 1, "title": "quis ut nam facilis", "completed": True},
    {"id": 3, "userId": 1, "title": "fugiat veniam minus", "completed": False},
]


# ---------------------------------------------------------------------------
# Flask app fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """Create a Flask test application with TestingConfig."""
    flask_app = create_app(TestingConfig)
    yield flask_app


@pytest.fixture
def client(app):
    """Return a Flask test client."""
    return app.test_client()
