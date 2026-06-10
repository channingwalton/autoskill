"""Dict-based API over the storage layer."""

from contacts.models import Customer
from contacts.storage import load_customer, save_customer


def create_customer(customer_id, name):
    """Create and store a customer, returning it as a dict."""
    customer = Customer(customer_id, name)
    save_customer(customer)
    return _to_dict(customer)


def get_customer(customer_id):
    """Return a stored customer as a dict."""
    return _to_dict(load_customer(customer_id))


def _to_dict(customer):
    return {"customer_id": customer.customer_id, "name": customer.name}
