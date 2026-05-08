"""
Unit tests for CustomerService (Business Logic Layer).

The database / repository is fully mocked using ``unittest.mock`` so these
tests run without any database connection and are extremely fast.

Test coverage
-------------
* get_all_customers
* get_customer         – found / not found
* create_customer      – success / missing field / duplicate e-mail
* update_customer      – success / not found / duplicate e-mail
* delete_customer      – success / not found
"""

from unittest.mock import MagicMock, patch
import pytest

from services.customer_service import (
    CustomerService,
    CustomerNotFoundError,
    DuplicateEmailError,
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _make_customer(id=1, name="Alice", email="alice@example.com", phone="111"):
    """Return a mock Customer ORM instance."""
    customer = MagicMock()
    customer.id = id
    customer.name = name
    customer.email = email
    customer.phone = phone
    customer.to_dict.return_value = {
        "id": id, "name": name, "email": email, "phone": phone,
    }
    return customer


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #

@pytest.fixture
def mock_repo():
    """Return a fully mocked CustomerRepository."""
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    """Return a CustomerService wired with the mock repository."""
    return CustomerService(repository=mock_repo)


# --------------------------------------------------------------------------- #
# get_all_customers
# --------------------------------------------------------------------------- #

class TestGetAllCustomers:
    def test_returns_list_of_dicts(self, service, mock_repo):
        mock_repo.get_all.return_value = [
            _make_customer(1, "Alice", "a@x.com", "1"),
            _make_customer(2, "Bob",   "b@x.com", "2"),
        ]
        result = service.get_all_customers()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Alice"

    def test_empty_list(self, service, mock_repo):
        mock_repo.get_all.return_value = []
        assert service.get_all_customers() == []


# --------------------------------------------------------------------------- #
# get_customer
# --------------------------------------------------------------------------- #

class TestGetCustomer:
    def test_returns_dict_for_existing_id(self, service, mock_repo):
        mock_repo.get_by_id.return_value = _make_customer()
        result = service.get_customer(1)
        assert result["id"] == 1

    def test_raises_not_found_for_missing_id(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(CustomerNotFoundError):
            service.get_customer(99)


# --------------------------------------------------------------------------- #
# create_customer
# --------------------------------------------------------------------------- #

class TestCreateCustomer:
    def test_creates_successfully(self, service, mock_repo):
        mock_repo.get_by_email.return_value = None
        mock_repo.create.return_value = _make_customer()
        data = {"name": "Alice", "email": "alice@example.com", "phone": "111"}
        result = service.create_customer(data)
        mock_repo.create.assert_called_once_with(
            name="Alice", email="alice@example.com", phone="111"
        )
        assert result["email"] == "alice@example.com"

    def test_raises_value_error_on_missing_field(self, service, mock_repo):
        with pytest.raises(ValueError, match="Missing required fields"):
            service.create_customer({"name": "X", "email": "x@x.com"})  # no phone

    def test_raises_duplicate_email(self, service, mock_repo):
        mock_repo.get_by_email.return_value = _make_customer()  # already exists
        with pytest.raises(DuplicateEmailError):
            service.create_customer(
                {"name": "Copy", "email": "alice@example.com", "phone": "000"}
            )

    def test_optional_address_passed_through(self, service, mock_repo):
        mock_repo.get_by_email.return_value = None
        mock_repo.create.return_value = _make_customer()
        service.create_customer(
            {"name": "Alice", "email": "alice@example.com", "phone": "111"}
        )
        mock_repo.create.assert_called_once_with(
            name="Alice", email="alice@example.com", phone="111"
        )


# --------------------------------------------------------------------------- #
# update_customer
# --------------------------------------------------------------------------- #

class TestUpdateCustomer:
    def test_updates_name_successfully(self, service, mock_repo):
        existing = _make_customer()
        mock_repo.get_by_id.return_value = existing
        updated = _make_customer(name="Alicia")
        mock_repo.update.return_value = updated
        result = service.update_customer(1, {"name": "Alicia"})
        assert result["name"] == "Alicia"

    def test_raises_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(CustomerNotFoundError):
            service.update_customer(99, {"name": "Ghost"})

    def test_raises_duplicate_email_on_update(self, service, mock_repo):
        existing = _make_customer(id=1, email="alice@example.com")
        other = _make_customer(id=2, email="bob@example.com")
        mock_repo.get_by_id.return_value = existing
        mock_repo.get_by_email.return_value = other  # new email is taken
        with pytest.raises(DuplicateEmailError):
            service.update_customer(1, {"email": "bob@example.com"})

    def test_same_email_does_not_trigger_duplicate_check(self, service, mock_repo):
        existing = _make_customer(email="alice@example.com")
        mock_repo.get_by_id.return_value = existing
        mock_repo.update.return_value = existing
        # Providing the same e-mail should NOT raise
        service.update_customer(1, {"email": "alice@example.com"})
        mock_repo.get_by_email.assert_not_called()


# --------------------------------------------------------------------------- #
# delete_customer
# --------------------------------------------------------------------------- #

class TestDeleteCustomer:
    def test_deletes_successfully(self, service, mock_repo):
        existing = _make_customer()
        mock_repo.get_by_id.return_value = existing
        result = service.delete_customer(1)
        mock_repo.delete.assert_called_once_with(existing)
        assert "message" in result

    def test_raises_not_found(self, service, mock_repo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(CustomerNotFoundError):
            service.delete_customer(99)
