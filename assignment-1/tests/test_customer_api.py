import pytest
from app.main import app

@pytest.fixture
def client():
	with app.test_client() as client:
		yield client

def test_get_all_customers(client):
	response = client.get('/customers')
	assert response.status_code == 200
	assert isinstance(response.get_json(), list)

def test_get_customer_by_id(client):
	response = client.get('/customers/1')
	assert response.status_code == 200
	data = response.get_json()
	assert data['id'] == 1

def test_create_customer(client):
	new_customer = {"name": "David", "email": "david@example.com", "phone": "456-789-0123"}
	response = client.post('/customers', json=new_customer)
	assert response.status_code == 201
	data = response.get_json()
	assert data['name'] == "David"

def test_update_customer(client):
	update_data = {"name": "Alice Updated"}
	response = client.put('/customers/1', json=update_data)
	assert response.status_code == 200
	data = response.get_json()
	assert data['name'] == "Alice Updated"

def test_delete_customer(client):
	response = client.delete('/customers/2')
	assert response.status_code == 200
	assert response.get_json()['message'] == 'Customer deleted'
