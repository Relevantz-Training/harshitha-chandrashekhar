"""
Customer Service (Business Logic Layer).

Sits between the HTTP routes and the data-access repository.  All business
rules – validation, duplicate-email checks, etc. – live here so that they
can be tested independently of both HTTP and the database.
"""

from repositories.customer_repository import CustomerRepository


class CustomerNotFoundError(Exception):
    """Raised when a requested customer does not exist."""


class DuplicateEmailError(Exception):
    """Raised when an e-mail address is already registered."""


class CustomerService:
    """
    Service class that orchestrates customer CRUD operations.

    Depends on ``CustomerRepository`` for data access; all business
    validation is handled before delegating persistence work.
    """

    def __init__(self, repository: CustomerRepository = None):
        """
        Initialise the service with an optional repository.

        Args:
            repository: A ``CustomerRepository`` instance (or compatible
                mock).  Defaults to a fresh ``CustomerRepository`` if not
                provided – useful for production; override in tests.
        """
        self.repo = repository or CustomerRepository()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_all_customers(self):
        """
        Return all customers as a list of dictionaries.

        Returns:
            list[dict]: Serialised list of all customer records.
        """
        return [c.to_dict() for c in self.repo.get_all()]

    def get_customer(self, customer_id: int):
        """
        Return a single customer by ID.

        Args:
            customer_id (int): Primary key of the customer.

        Returns:
            dict: Serialised customer data.

        Raises:
            CustomerNotFoundError: If no customer with the given ID exists.
        """
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(
                f"Customer with id={customer_id} not found."
            )
        return customer.to_dict()

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_customer(self, data: dict):
        """
        Validate and create a new customer.

        Required keys in *data*: ``name``, ``email``, ``phone``.
        Optional key: ``address``.

        Args:
            data (dict): Payload containing customer fields.

        Returns:
            dict: Serialised data of the newly created customer.

        Raises:
            ValueError: If any required field is missing or empty.
            DuplicateEmailError: If the e-mail is already registered.
        """
        required = ("name", "email", "phone")
        missing = [f for f in required if not data.get(f)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        # Business rule: e-mail must be unique
        if self.repo.get_by_email(data["email"]):
            raise DuplicateEmailError(
                f"Email '{data['email']}' is already registered."
            )

        customer = self.repo.create(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
        )
        return customer.to_dict()

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update_customer(self, customer_id: int, data: dict):
        """
        Update an existing customer's details.

        Only keys present in *data* are updated; others retain their
        current values.

        Args:
            customer_id (int): Primary key of the customer to update.
            data        (dict): Fields to update.

        Returns:
            dict: Serialised updated customer data.

        Raises:
            CustomerNotFoundError: If the customer does not exist.
            DuplicateEmailError: If the new e-mail is already taken by
                another customer.
        """
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(
                f"Customer with id={customer_id} not found."
            )

        new_email = data.get("email")
        if new_email and new_email != customer.email:
            existing = self.repo.get_by_email(new_email)
            if existing:
                raise DuplicateEmailError(
                    f"Email '{new_email}' is already registered."
                )

        updated = self.repo.update(
            customer,
            name=data.get("name"),
            email=new_email,
            phone=data.get("phone"),
        )
        return updated.to_dict()

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_customer(self, customer_id: int):
        """
        Delete a customer by ID.

        Args:
            customer_id (int): Primary key of the customer to delete.

        Returns:
            dict: Confirmation message.

        Raises:
            CustomerNotFoundError: If the customer does not exist.
        """
        customer = self.repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(
                f"Customer with id={customer_id} not found."
            )
        self.repo.delete(customer)
        return {"message": f"Customer id={customer_id} deleted successfully."}
