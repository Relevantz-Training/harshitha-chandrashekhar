"""
Integration tests for the Customer REST API.

Uses Flask's test client with an in-memory SQLite database so tests are
fully isolated – no external database is required.

Test coverage
-------------
* GET  /customers          – list all
* GET  /customers/<id>     – found / not found
* POST /customers          – success / missing field / duplicate e-mail
* PUT  /customers/<id>     – success / not found / duplicate e-mail
* DELETE /customers/<id>   – success / not found
"""

import pytest
from main import create_app
from database import db as _db


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def app():
    """
    Create a Flask app configured for testing.

    Uses an in-memory SQLite database; tables are created once per module and
    dropped at teardown.
    """
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    """Return a Flask test client."""
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_tables(app):
    """
    Truncate the customers table before every test to guarantee isolation.
    """
    with app.app_context():
        from models.customer import Customer
        _db.session.query(Customer).delete()
        _db.session.commit()


@pytest.fixture
def seeded_client(client, app):
    """
    A test client pre-loaded with three sample customers.

    Returns:
        tuple[FlaskClient, list[dict]]: The test client and the list of
        created customer dicts.
    """
    customers = [
        {"name": "Alice Smith", "email": "alice@example.com", "phone": "111-111-1111"},
        {"name": "Bob Jones",   "email": "bob@example.com",   "phone": "222-222-2222"},
        {"name": "Carol White", "email": "carol@example.com", "phone": "333-333-3333"},
    ]
    created = []
    for payload in customers:
        resp = client.post("/customers", json=payload)
        assert resp.status_code == 201, f"Seed failed: {resp.get_json()}"
        created.append(resp.get_json())
    return client, created


# --------------------------------------------------------------------------- #
# GET /customers
# --------------------------------------------------------------------------- #

class TestListCustomers:
    """Tests for GET /customers."""

    def test_empty_list(self, client):
        """Should return an empty array when no customers exist."""
        response = client.get("/customers")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_all_customers(self, seeded_client):
        """Should return all seeded customers."""
        c, created = seeded_client
        response = c.get("/customers")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 3


# --------------------------------------------------------------------------- #
# GET /customers/<id>
# --------------------------------------------------------------------------- #

class TestGetCustomer:
    """Tests for GET /customers/<id>."""

    def test_get_existing_customer(self, seeded_client):
        """Should return 200 with the correct customer."""
        c, created = seeded_client
        customer_id = created[0]["id"]
        response = c.get(f"/customers/{customer_id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["email"] == "alice@example.com"

    def test_get_nonexistent_customer(self, client):
        """Should return 404 for an unknown ID."""
        response = client.get("/customers/9999")
        assert response.status_code == 404
        assert "error" in response.get_json()


# --------------------------------------------------------------------------- #
# POST /customers
# --------------------------------------------------------------------------- #

class TestCreateCustomer:
    """Tests for POST /customers."""

    def test_create_success(self, client):
        """Should create a customer and return 201 with the new record."""
        payload = {
            "name": "Dave Brown",
            "email": "dave@example.com",
            "phone": "444-444-4444",
        }
        response = client.post("/customers", json=payload)
        assert response.status_code == 201
        data = response.get_json()
        assert data["id"] is not None
        assert data["name"] == "Dave Brown"

    def test_create_missing_required_field(self, client):
        """Should return 400 when a required field is absent."""
        payload = {"name": "Eve", "email": "eve@example.com"}  # phone missing
        response = client.post("/customers", json=payload)
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_create_duplicate_email(self, seeded_client):
        """Should return 409 when the e-mail is already registered."""
        c, _ = seeded_client
        payload = {"name": "Alice Copy", "email": "alice@example.com", "phone": "000-000-0000"}
        response = c.post("/customers", json=payload)
        assert response.status_code == 409
        assert "error" in response.get_json()

    def test_create_no_body(self, client):
        """Should return 400 when no JSON body is provided."""
        response = client.post("/customers", content_type="application/json", data="")
        assert response.status_code == 400


# --------------------------------------------------------------------------- #
# PUT /customers/<id>
# --------------------------------------------------------------------------- #

class TestUpdateCustomer:
    """Tests for PUT /customers/<id>."""

    def test_update_name(self, seeded_client):
        """Should update the name and return the updated record."""
        c, created = seeded_client
        customer_id = created[1]["id"]
        response = c.put(f"/customers/{customer_id}", json={"name": "Robert Jones"})
        assert response.status_code == 200
        assert response.get_json()["name"] == "Robert Jones"

    def test_update_nonexistent_customer(self, client):
        """Should return 404 for an unknown customer."""
        response = client.put("/customers/9999", json={"name": "Ghost"})
        assert response.status_code == 404

    def test_update_duplicate_email(self, seeded_client):
        """Should return 409 if the new e-mail belongs to another customer."""
        c, created = seeded_client
        customer_id = created[1]["id"]
        response = c.put(
            f"/customers/{customer_id}",
            json={"email": "alice@example.com"},  # already taken by created[0]
        )
        assert response.status_code == 409

    def test_update_no_body(self, seeded_client):
        """Should return 400 when no JSON body is provided."""
        c, created = seeded_client
        response = c.put(
            f"/customers/{created[0]['id']}",
            content_type="application/json",
            data="",
        )
        assert response.status_code == 400


# --------------------------------------------------------------------------- #
# DELETE /customers/<id>
# --------------------------------------------------------------------------- #

class TestDeleteCustomer:
    """Tests for DELETE /customers/<id>."""

    def test_delete_existing_customer(self, seeded_client):
        """Should delete the customer and return 200 with a message."""
        c, created = seeded_client
        customer_id = created[2]["id"]
        response = c.delete(f"/customers/{customer_id}")
        assert response.status_code == 200
        assert "message" in response.get_json()

        # Confirm deletion
        get_resp = c.get(f"/customers/{customer_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_customer(self, client):
        """Should return 404 for an unknown customer."""
        response = client.delete("/customers/9999")
        assert response.status_code == 404
