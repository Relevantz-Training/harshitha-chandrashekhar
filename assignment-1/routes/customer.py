from flask import Blueprint, jsonify, request
from app.models.customer import Customer, mock_customers

customer_bp = Blueprint('customer_bp', __name__)
"""Blueprint for customer CRUD API routes."""

# Get all customers
@customer_bp.route('/customers', methods=['GET'])
def get_customers():
	"""Return all customers."""
	return jsonify([c.to_dict() for c in mock_customers]), 200

# Get a customer by ID
@customer_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
	"""Return a customer by ID."""
	customer = next((c for c in mock_customers if c.id == customer_id), None)
	if customer:
		return jsonify(customer.to_dict()), 200
	return jsonify({'error': 'Customer not found'}), 404

# Create a new customer
@customer_bp.route('/customers', methods=['POST'])
def create_customer():
	"""Create a new customer."""
	data = request.get_json()
	if not data or not all(k in data for k in ('name', 'email', 'phone')):
		return jsonify({'error': 'Invalid data'}), 400
	new_id = max([c.id for c in mock_customers], default=0) + 1
	customer = Customer(new_id, data['name'], data['email'], data['phone'])
	mock_customers.append(customer)
	return jsonify(customer.to_dict()), 201

# Update an existing customer
@customer_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
	"""Update an existing customer."""
	data = request.get_json()
	customer = next((c for c in mock_customers if c.id == customer_id), None)
	if not customer:
		return jsonify({'error': 'Customer not found'}), 404
	customer.name = data.get('name', customer.name)
	customer.email = data.get('email', customer.email)
	customer.phone = data.get('phone', customer.phone)
	return jsonify(customer.to_dict()), 200

# Delete a customer
@customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
	"""Delete a customer by ID."""
	global mock_customers
	customer = next((c for c in mock_customers if c.id == customer_id), None)
	if not customer:
		return jsonify({'error': 'Customer not found'}), 404
	mock_customers.remove(customer)
	return jsonify({'message': 'Customer deleted'}), 200
