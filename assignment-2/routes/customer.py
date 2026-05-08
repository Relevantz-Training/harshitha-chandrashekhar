"""
Customer HTTP Routes (Presentation Layer).

Defines a Flask Blueprint with RESTful endpoints for the Customer CRUD API.
All business logic is delegated to ``CustomerService``; this layer is
responsible only for request parsing, HTTP status codes, and JSON responses.

Endpoints
---------
GET    /customers          – List all customers
GET    /customers/<id>     – Get a customer by ID
POST   /customers          – Create a new customer
PUT    /customers/<id>     – Update an existing customer
DELETE /customers/<id>     – Delete a customer
"""

from flask import Blueprint, jsonify, request
from services.customer_service import (
    CustomerService,
    CustomerNotFoundError,
    DuplicateEmailError,
)

customer_bp = Blueprint("customer_bp", __name__, url_prefix="/customers")

# Shared service instance (can be overridden in tests via monkey-patching)
_service = CustomerService()


def get_service() -> CustomerService:
    """Return the active CustomerService instance."""
    return _service


# --------------------------------------------------------------------------- #
# GET /customers
# --------------------------------------------------------------------------- #

@customer_bp.route("", methods=["GET"])
def list_customers():
    """
    Retrieve all customers.

    Returns:
        200 OK – JSON array of all customer objects.
    """
    customers = get_service().get_all_customers()
    return jsonify(customers), 200


# --------------------------------------------------------------------------- #
# GET /customers/<id>
# --------------------------------------------------------------------------- #

@customer_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id: int):
    """
    Retrieve a single customer by ID.

    Args:
        customer_id (int): Customer primary key (path parameter).

    Returns:
        200 OK      – JSON customer object.
        404 Not Found – ``{"error": "<message>"}`` if not found.
    """
    try:
        customer = get_service().get_customer(customer_id)
        return jsonify(customer), 200
    except CustomerNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404


# --------------------------------------------------------------------------- #
# POST /customers
# --------------------------------------------------------------------------- #

@customer_bp.route("", methods=["POST"])
def create_customer():
    """
    Create a new customer.

    Request Body (JSON):
        name    (str, required)
        email   (str, required)
        phone   (str, required)
        address (str, optional)

    Returns:
        201 Created  – JSON of the newly created customer.
        400 Bad Request – Validation error message.
        409 Conflict    – Duplicate e-mail error message.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400
    try:
        customer = get_service().create_customer(data)
        return jsonify(customer), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except DuplicateEmailError as exc:
        return jsonify({"error": str(exc)}), 409


# --------------------------------------------------------------------------- #
# PUT /customers/<id>
# --------------------------------------------------------------------------- #

@customer_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id: int):
    """
    Update an existing customer.

    Args:
        customer_id (int): Customer primary key (path parameter).

    Request Body (JSON):
        Any subset of: name, email, phone, address.

    Returns:
        200 OK          – JSON of the updated customer.
        400 Bad Request – Missing / invalid payload.
        404 Not Found   – Customer does not exist.
        409 Conflict    – Duplicate e-mail.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400
    try:
        customer = get_service().update_customer(customer_id, data)
        return jsonify(customer), 200
    except CustomerNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except DuplicateEmailError as exc:
        return jsonify({"error": str(exc)}), 409


# --------------------------------------------------------------------------- #
# DELETE /customers/<id>
# --------------------------------------------------------------------------- #

@customer_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id: int):
    """
    Delete a customer by ID.

    Args:
        customer_id (int): Customer primary key (path parameter).

    Returns:
        200 OK        – ``{"message": "..."}`` confirmation.
        404 Not Found – Customer does not exist.
    """
    try:
        result = get_service().delete_customer(customer_id)
        return jsonify(result), 200
    except CustomerNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
