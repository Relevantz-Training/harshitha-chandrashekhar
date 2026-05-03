# Customer model and mock data will be defined here
"""
Customer model and mock data for the CRUD API.
"""


class Customer:
	"""Represents a customer with id, name, email, and phone."""
	def __init__(self, id, name, email, phone):
		self.id = id
		self.name = name
		self.email = email
		self.phone = phone

	def to_dict(self):
		"""Return customer data as a dictionary."""
		return {
			"id": self.id,
			"name": self.name,
			"email": self.email,
			"phone": self.phone
		}

# Mock customer data for testing
mock_customers = [
	Customer(1, "Alice Smith", "alice@example.com", "123-456-7890"),
	Customer(2, "Bob Johnson", "bob@example.com", "234-567-8901"),
	Customer(3, "Charlie Lee", "charlie@example.com", "345-678-9012")
]
