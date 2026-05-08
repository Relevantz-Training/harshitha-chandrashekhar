"""
Customer Repository (Data Access Layer).

Encapsulates all direct database interactions for the Customer entity.
The rest of the application never imports ``db`` or ``Customer`` directly
– it always goes through this repository, making it easy to swap the
underlying storage engine without touching business logic or routes.
"""

from database import db
from models.customer import Customer


class CustomerRepository:
    """
    Repository providing CRUD operations for the ``Customer`` model.

    All methods interact with the SQLAlchemy session / database directly.
    """

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    @staticmethod
    def get_all():
        """
        Retrieve all customers from the database.

        Returns:
            list[Customer]: A list of all Customer ORM instances.
        """
        return Customer.query.all()

    @staticmethod
    def get_by_id(customer_id: int):
        """
        Retrieve a single customer by primary key.

        Args:
            customer_id (int): The customer's primary key.

        Returns:
            Customer | None: The matching Customer instance, or ``None`` if
            not found.
        """
        return db.session.get(Customer, customer_id)

    @staticmethod
    def get_by_email(email: str):
        """
        Retrieve a customer by their unique e-mail address.

        Args:
            email (str): The e-mail address to search for.

        Returns:
            Customer | None: The matching Customer instance, or ``None``.
        """
        return Customer.query.filter_by(email=email).first()

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    @staticmethod
    def create(name: str, email: str, phone: str):
        """
        Insert a new customer record into the database.

        Args:
            name  (str): Full name of the customer.
            email (str): Unique e-mail address.
            phone (str): Contact phone number.

        Returns:
            Customer: The newly created and persisted Customer instance.
        """
        customer = Customer(name=name, email=email, phone=phone)
        db.session.add(customer)
        db.session.commit()
        return customer

    @staticmethod
    def update(customer: Customer, name: str = None, email: str = None,
               phone: str = None):
        """
        Update one or more fields of an existing customer.

        Only fields that are explicitly provided (not ``None``) will be
        updated, preserving the existing values for omitted fields.

        Args:
            customer (Customer): The ORM instance to update.
            name     (str, optional): New full name.
            email    (str, optional): New e-mail address.
            phone    (str, optional): New phone number.

        Returns:
            Customer: The updated Customer instance after commit.
        """
        if name is not None:
            customer.name = name
        if email is not None:
            customer.email = email
        if phone is not None:
            customer.phone = phone
        db.session.commit()
        return customer

    @staticmethod
    def delete(customer: Customer):
        """
        Remove a customer record from the database.

        Args:
            customer (Customer): The ORM instance to delete.
        """
        db.session.delete(customer)
        db.session.commit()
