# Assignment 2 – Customer CRUD API with Database Integration

## Overview

An enhanced version of Assignment-1 that replaces the in-memory mock store with
a real **SQLite** database (via **Flask-SQLAlchemy**).  The project follows a
clean, layered architecture:

```
HTTP Request
    │
    ▼
┌─────────────────────────────┐
│  Routes  (routes/)          │  ← HTTP concerns only
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Service  (services/)       │  ← Business logic & validation
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  Repository (repositories/) │  ← Data-access abstraction
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  ORM Model (models/)        │  ← SQLAlchemy table mapping
└─────────────────────────────┘
             │
             ▼
      SQLite / Database
```

## Project Structure

```
assignment-2/
├── main.py                         # App factory & entry point
├── config.py                       # Dev / Test / Prod configurations
├── database.py                     # SQLAlchemy instance
├── requirements.txt
├── pytest.ini
├── models/
│   └── customer.py                 # Customer ORM model
├── repositories/
│   └── customer_repository.py      # Data-access layer
├── services/
│   └── customer_service.py         # Business-logic layer
├── routes/
│   └── customer.py                 # Flask Blueprint (REST endpoints)
└── tests/
    ├── conftest.py
    ├── test_customer_api.py        # Integration tests (in-memory DB)
    └── test_customer_service.py    # Unit tests (mocked repository)
```

## Prerequisites

- Python 3.9+
- pip

## Installation

```bash
cd assignment-2
pip install -r requirements.txt
```

## Running the API

```bash
python main.py
```

The server starts at `http://127.0.0.1:5000`.  
Three sample customers are auto-seeded on first run (development mode).

## API Endpoints

| Method | Endpoint              | Description               |
|--------|-----------------------|---------------------------|
| GET    | `/customers`          | List all customers        |
| GET    | `/customers/<id>`     | Get customer by ID        |
| POST   | `/customers`          | Create a new customer     |
| PUT    | `/customers/<id>`     | Update a customer         |
| DELETE | `/customers/<id>`     | Delete a customer         |

### Request / Response examples

#### Create a customer
```http
POST /customers
Content-Type: application/json

{
  "name":    "Jane Doe",
  "email":   "jane@example.com",
  "phone":   "555-123-4567",
  "address": "42 Maple Ave"   ← optional
}
```
```json
HTTP 201 Created
{
  "id": 4,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "555-123-4567",
  "address": "42 Maple Ave"
}
```

#### Update a customer
```http
PUT /customers/4
Content-Type: application/json

{ "phone": "555-999-0000" }
```

#### Delete a customer
```http
DELETE /customers/4
```
```json
{ "message": "Customer id=4 deleted successfully." }
```

## Running Tests

```bash
pytest -v
```

- **`test_customer_service.py`** – pure unit tests; repository is mocked with
  `unittest.mock`, no database involved.
- **`test_customer_api.py`** – integration tests using Flask's test client and an
  in-memory SQLite database; full request→response cycle is tested.

## Key Enhancements over Assignment-1

| Feature                   | Assignment-1      | Assignment-2               |
|---------------------------|-------------------|----------------------------|
| Data storage              | In-memory list    | SQLite via SQLAlchemy ORM  |
| Architecture layers       | 2 (model + route) | 4 (model, repo, service, route) |
| Validation                | Minimal           | Service-layer validation   |
| Duplicate e-mail guard    | ✗                 | ✔                          |
| Address field             | ✗                 | ✔ (optional)               |
| Environment configs       | ✗                 | Dev / Test / Prod          |
| Unit tests (mocked)       | ✗                 | ✔ `test_customer_service`  |
| Integration tests         | ✔                 | ✔ `test_customer_api`      |
| Dev seed data             | Hard-coded mock   | Auto-seeded to DB          |
