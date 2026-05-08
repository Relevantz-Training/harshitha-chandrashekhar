"""
Customer ORM model.

Defines the ``Customer`` SQLAlchemy model that maps directly to the
``customers`` table in the configured relational database.
"""

from database import db


class Customer(db.Model):
    """
    SQLAlchemy ORM model for the ``customers`` table.

    Attributes:
        id      (int):  Primary key, auto-incremented.
        name    (str):  Full name of the customer (max 100 chars).
        email   (str):  Unique e-mail address (max 120 chars).
        phone   (str):  Contact phone number (max 20 chars).
        address (str):  Optional street / city address (max 200 chars).
    """

    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        """
        Serialise the model instance to a plain Python dictionary.

        Returns:
            dict: A JSON-serialisable representation of the customer.
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
        }

    def __repr__(self):
        return f"<Customer id={self.id} name='{self.name}' email='{self.email}'>"
