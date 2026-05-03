## Assignment Description

**Exercise:**

Create a CRUD API on customer details table with proper project structure which emphasizes unit test cases and documentation. (Use mock data within the project)

---

# Customer CRUD API (Flask)

A simple Python Flask API for managing customer details with in-memory mock data. Includes full CRUD operations, unit tests, and clear documentation.

**Instructions:**
- Use Python as the preferred language
- Use mock data (no real database)
- Organize code with models, routes, and tests
- Include unit tests and documentation

---

## Features
- Create, Read, Update, Delete (CRUD) for customers
- Organized project structure
- Unit tests with pytest
- Easy to run and test

---


## Setup & Installation

If you are using this project for the first time (after downloading or cloning):

1. **(For others) Clone the repository**
   ```
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```
   *(If you built the project locally, skip this step.)*

2. **Create a virtual environment**
   ```
   python -m venv venv
   ```
3. **Activate the virtual environment**
   - On Windows:
     ```
     .\venv\Scripts\activate
     ```
   - On Mac/Linux:
     ```
     source venv/bin/activate
     ```
4. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```
---

## Uploading Your Local Project to GitHub

If you built this project locally and want to upload it to your GitHub account:

1. **Initialize git (if not already done):**
   ```
   git init
   ```
2. **Add all files:**
   ```
   git add .
   ```
3. **Commit your changes:**
   ```
   git commit -m "Initial commit: Customer CRUD API assignment"
   ```
4. **Create a new repository on GitHub** (in your browser, on your account).
5. **Connect your local repo to GitHub:**
   ```
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   ```
6. **Push your code:**
   ```
   git branch -M main
   git push -u origin main
   ```

---

---

## Running the App

Start the Flask server:
```
python -m app.main
```
The API will be available at `http://127.0.0.1:5000/`

---

## Running Tests

Run all unit tests with:
```
pytest
```

If you see import errors, try:
```
$env:PYTHONPATH = "."
pytest
```

---

## API Endpoints

- `GET /customers` - List all customers
- `GET /customers/<id>` - Get customer by ID
- `POST /customers` - Create new customer (JSON: name, email, phone)
- `PUT /customers/<id>` - Update customer (JSON: name, email, phone)
- `DELETE /customers/<id>` - Delete customer

---

## Project Structure

```
your-project/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   └── customer.py
│   └── routes/
│       └── customer.py
│
├── tests/
│   └── test_customer_api.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

---

## Prompts & Notes

- All code, setup, and test steps are included in this README for easy reference.
- For any issues, check the docstrings in the code or contact your instructor.

---

## License

MIT
